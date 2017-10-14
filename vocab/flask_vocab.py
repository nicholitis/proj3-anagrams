"""
Flask web site with vocabulary matching game
(identify vocabulary words that can be made 
from a scrambled string)
"""
import flask
from flask import request
from flask import url_for
from flask import jsonify
import logging
import argparse
# Our own modules
from letterbag import LetterBag
from vocab import Vocab
from jumble import jumbled
import config

###
# Globals
###
app = flask.Flask(__name__)

CONFIG = config.configuration()
app.secret_key = CONFIG.SECRET_KEY  # Should allow using session variables

#
# One shared 'Vocab' object, read-only after initialization,
# shared by all threads and instances.  Otherwise we would have to
# store it in the browser and transmit it on each request/response cycle,
# or else read it from the file on each request/responce cycle,
# neither of which would be suitable for responding keystroke by keystroke.

WORDS = Vocab(CONFIG.VOCAB)

###
# Pages
###


@app.route("/")
@app.route("/index")
def index():
    """The main page of the application"""
    flask.g.vocab = WORDS.as_list()
    flask.session["target_count"] = min(
        len(flask.g.vocab), CONFIG.SUCCESS_AT_COUNT)
    flask.session["jumble"] = jumbled(
        flask.g.vocab, flask.session["target_count"])
    flask.session["matches"] = []
    app.logger.debug("Session variables have been set")
    assert flask.session["matches"] == []
    assert flask.session["target_count"] > 0
    app.logger.debug("At least one seems to be set correctly")
    return flask.render_template('vocab.html')


@app.route("/keep_going")
def keep_going():
    """
    After initial use of index, we keep the same scrambled
    word and try to get more matches
    """
    flask.g.vocab = WORDS.as_list()
    return flask.render_template('vocab.html')


@app.route("/success")
def success():
    return flask.render_template('success.html')

#######################
# Form handler.
# CIS 322 note:
#   You'll need to change this to a
#   a JSON request handler
#######################


@app.route("/_check")
def check():
    """
    basically instead of returning flash to reload the page this function
    returns json to maintain a dynamic webpage rather than cycling 
    through static pages every game move. conditional logic is pretty much
    unchanged.
    """
    app.logger.debug("Entering check")

    # The data we need, from form and from cookie
    text = flask.request.args.get("text", type=str)
    jumble = flask.session["jumble"]
    matches = flask.session.get("matches", [])

    # Is it good?
    in_jumble = LetterBag(jumble).contains(text)
    matched = WORDS.has(text)

    # Respond appropriately
    if matched and in_jumble and not (text in matches):
        # Cool, they found a new word
        matches.append(text)
        flask.session["matches"] = matches
    elif text in matches:
        alert = "You already found {}".format(text)
        rslt = {"alert": alert}
        return jsonify(result=rslt)
    elif not matched:
        alert = "\'{}\' isn't in the list of words".format(text)
        rslt = {"alert": alert}
        return jsonify(result=rslt)
    elif not in_jumble:
        alert = '"{}" can\'t be made from the letters {}'.format(text,jumble)
        rslt = {"alert": alert}
        return jsonify(result=rslt)
    else:
        app.logger.debug("This case shouldn't happen!")
        assert False  # Raises AssertionError


###############
# AJAX request handlers
#   These return JSON, rather than rendering pages.
###############


@app.route("/_example")
def example():
    """
    Example ajax request handler
    """
    app.logger.debug("Got a JSON request")
    rslt = {"key": "value"}
    return flask.jsonify(result=rslt)

@app.route("/_solved")
def solved():
    """
    updates page when a new word is found. most of this code is copy/pasted
    from the "check" function or the minijax .py script. the bottom bit is 
    basically the bottom of the original if conditional from "check" as well.
    """

    ## The data we need, from form and from cookie
    text = request.args.get("text", type=str)
    jumble = flask.session["jumble"]
    matches = flask.session.get("matches", []) # Default to empty list

    ## Is it good?
    in_jumble = LetterBag(jumble).contains(text)
    matched = WORDS.has(text)

    if matched and in_jumble and not (text in matches):
        matches.append(text)
        flask.session["matches"] = matches
    if len(matches) >= flask.session["target_count"]:
        #matched 3 words
        rslt = { "function": "/success"}
        return jsonify(result=rslt)
    else:
        #yet to match 3 words
        rslt = { "function": "/keep_going" }
        return jsonify(result=rslt)

@app.route("/_correct")
def correct():
    '''
    checks input validity
    '''
    app.logger.debug("Entering check")
    text = request.args.get("text", type=str)
    matches = flask.session.get("matches", [])
    jumble = flask.session["jumble"]
    matched = WORDS.has(text)
    in_jumble = LetterBag(jumble).contains(text)

    if matched and in_jumble:
        userinput = True
    else:
        userinput = False

    if text in matches:
        userinput = False

    rslt = { "userinput": userinput }
    return jsonify(result=rslt)


#################
# Functions used within the templates
#################

@app.template_filter('filt')
def format_filt(something):
    """
    Example of a filter that can be used within
    the Jinja2 code
    """
    return "Not what you asked for"

###################
#   Error handlers
###################


@app.errorhandler(404)
def error_404(e):
    app.logger.warning("++ 404 error: {}".format(e))
    return flask.render_template('404.html'), 404


@app.errorhandler(500)
def error_500(e):
    app.logger.warning("++ 500 error: {}".format(e))
    assert not True  # I want to invoke the debugger
    return flask.render_template('500.html'), 500


@app.errorhandler(403)
def error_403(e):
    app.logger.warning("++ 403 error: {}".format(e))
    return flask.render_template('403.html'), 403


####

if __name__ == "__main__":
    if CONFIG.DEBUG:
        app.debug = True
        app.logger.setLevel(logging.DEBUG)
        app.logger.info(
            "Opening for global access on port {}".format(CONFIG.PORT))
        app.run(port=CONFIG.PORT, host="0.0.0.0")
