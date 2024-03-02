from flask import Flask, session, request, render_template, redirect, make_response, flash
from flask_debugtoolbar import DebugToolbarExtension
from surveys import surveys

# create a current
CURRENT_SURVEY_KEY = "current_survey"
RESPONSES_KEY = "responses"

app = Flask(__name__)
app.config['SECRET_KEY'] = "never-tell!"
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False

debug = DebugToolbarExtension(app)



@app.route("/")
def show_pick_survey_form():
    """Show pick survey form"""
    return render_template("pick-survey.html", surveys=surveys)

















@app.route("/", methods=["POST"])
def pick_survey():

    survey_id = request.form['survey_code']

    #don't let them re-take a survey until cookie times out
    if request.cookies.get(f"completed_{survey_id}"):
        return render_template("alredy-done.html")
    
    survey = surveys[survey_id]
    session[CURRENT_SURVEY_KEY] = survey_id

    return render_template("survey_start.html", survey=survey)




@app.route("/begin", methods=["POST"])
def start_survey():
    """Clear the sessiong of responeses"""

    #set the response key at the current sessiong to be empty
    session[RESPONSES_KEY] = []

    return redirect("/questions/0")







@app.route("/answer", methods=["POST"])
def handle_question():
    """Save response and redirect to next question"""
    choice = request.form['answer']
    text = request.form.get("text", "")

    # add this reponse to the list in the session
    responses = session[RESPONSES_KEY]
    responses.append({"choice": choice, "text": text})

    # add this response to the session
    session[RESPONSES_KEY] = responses
    survey_code = session[CURRENT_SURVEY_KEY]
    survey = surveys[survey_code]

    # if length of responses is the length of the survey  question
        # redirect to /complete
    #else 
        # redirect to "/questions/length of responses"
    
    if(len(responses) == len(survey.questions)):
        return redirect("/complete")
    else:
        return redirect(f"/question/{len(responses)}")
    


@app.route("/questions/<int:qid>")
def show_question(qid):
    """Display current question"""

    responses = session.get(RESPONSES_KEY)
    survey_code = session[CURRENT_SURVEY_KEY]
    survey = surveys[survey_code]

    #if there is no response:
        #redirect to main page
    if (responses is None):
        return redirect("/")
    
    #if length of responses is the len of the survey questions
        # this means they've completed the survery redirect them to complete, thank them
    if(len(responses) == len(survey.questions)):
        return redirect("/complete")
    
    # if length of responses does not equal "qid"
# Trying to access questions out of order
    #flash a message saying invalid question id {qid}
    # return redirect /questions/len of responses
    if (len(responses) != qid):
        # Trying to access questions out of order
        flash(f"Invalid question id {qid}.")
        return redirect(f"/questions/{len(responses)}")
    
    # question equales the current question id at the questions on the survey
    question = survey.questions[qid]

    #return question.html, question_num = qid, question=question
    return render_template('question.html', question_num = qid, question=question)



@app.route("/complete")
def say_thanks():
    """Thank user and list responses."""

    survey_id = session[CURRENT_SURVEY_KEY]
    survey = surveys[survey_id]
    responses = session[RESPONSES_KEY]

    html = render_template("completion.html",
                           survey=survey,
                           responses=responses)

    # Set cookie noting this survey is done so they can't re-do it
    response = make_response(html)
    response.set_cookie(f"completed_{survey_id}", "yes", max_age=60)
    return response