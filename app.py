import gradio as gr
import openai
from datetime import datetime
from pytz import timezone
from apscheduler.schedulers.background import BackgroundScheduler

TRIES = 10

def update_tries():
    print("TRIES have been reset.")
    global TRIES
    TRIES = 10

def main():

    # Configure scheduler to run update_tries() every day at midnight in Sydney timezone
    scheduler = BackgroundScheduler(timezone='Australia/Sydney')
    scheduler.add_job(update_tries, 'cron', hour=0, minute=0)
    scheduler.start()

    openai.api_key = open("key.txt", "r").read().strip("\n")

    message_history = [{"role": "user", "content": f"You are a research bot. I will specify the subject matter in my messages, and you will reply with the earliest research reference of the subject matter in my messages. Your reply should be the reference in APA format and nothing else. If you understand, say OK."},
                    {"role": "assistant", "content": f"OK"}]
    
    
    def predict(input):
        
        global TRIES
        if TRIES > 0:

            # tokenize the new input sentence
            message_history.append({"role": "user", "content": f"{input}"})

            completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=message_history
            )
            #Just the reply text
            reply_content = completion.choices[0].message.content
            #.replace('```python', '<pre>').replace('```', '</pre>')
            
            message_history.append({"role": "assistant", "content": f"{reply_content}"}) 

            TRIES = TRIES -1
        else :
            message_history.append({"role": "user", "content": f"{input}"})
            message_history.append({"role": "assistant", "content": "The daily usage limit has been reached, please check again tomorrow."}) 
            
            # get pairs of msg["content"] from message history, skipping the pre-prompt:              here.
        response = [(message_history[i]["content"], message_history[i+1]["content"]) for i in range(2, len(message_history)-1, 2)]  # convert to tuples of list
        # print(response)
        return response
    
    # creates a new Blocks app and assigns it to the variable demo.
    with gr.Blocks(title="Research Bot") as app: 

        gr.Markdown(
            """
        # Research Bot 🔬
        **Start typing a complex term below to see it's earliest reference.**
        As this bot is still in beta version, I will be grateful for any [feedback](https://forms.gle/L7cmV3b3rF8QoT347) you might have!  \
        And if you've found this bot helpful, would you kindly consider [buying me a coffee](https://www.buymeacoffee.com/ivanpuatomato?) ☕️ Your support would mean the world to me!
        """
        )

        # creates a new Chatbot instance and assigns it to the variable chatbot.
        chatbot = gr.Chatbot() 

        # creates a new Row component, which is a container for other components.
        with gr.Row(): 
            '''creates a new Textbox component, which is used to collect user input. 
            The show_label parameter is set to False to hide the label, 
            and the placeholder parameter is set'''
            txt = gr.Textbox(show_label=False, placeholder="e.g. Game Theory, Coronavirus, Neural Networks").style(container=False)
        
        '''
        sets the submit action of the Textbox to the predict function, 
        which takes the input from the Textbox, the chatbot instance, 
        and the state instance as arguments. 
        This function processes the input and generates a response from the chatbot, 
        which is displayed in the output area.'''
        txt.submit(predict, txt, chatbot) # submit(function, input, output)
        #txt.submit(lambda :"", None, txt)  #Sets submit action to lambda function that returns empty string 

        '''
        sets the submit action of the Textbox to a JavaScript function that returns an empty string. 
        This line is equivalent to the commented out line above, but uses a different implementation. 
        The _js parameter is used to pass a JavaScript function to the submit method.'''
        txt.submit(None, None, txt, _js="() => {''}") # No function, no input to that function, submit action to textbox is a js function that returns empty string, so it clears immediately.
            
    # demo.launch(share=True)
    app.launch()

if __name__ == "__main__":
    main()

