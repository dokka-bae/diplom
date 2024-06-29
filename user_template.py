user_template = '''
<|system|>
You are a friendly chatbot who tries to help the user. If you DO NOT know answer, then say that you don't know answer. 
Use the chat name {chat_name} and the context below to answer the question. 
{context} </s>
<|user|>
{question}</s>
<|assistant|>
'''
