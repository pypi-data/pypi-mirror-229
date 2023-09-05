from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Start, Stream

import openai


import vosk
import audioop
import base64
import json

import time

import threading


    
class Twilio:
    ACCOUNT_SID = None
    AUTH_TOKEN = None
    client = None
    call_sid = None
    stream_url = None
    new_command_timeout = 600
    
    def __init__(self, phone_gpt_object, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN):
        self.phone_gpt_object = phone_gpt_object        
        self.ACCOUNT_SID = TWILIO_ACCOUNT_SID
        self.AUTH_TOKEN = TWILIO_AUTH_TOKEN
        self.client = Client(self.ACCOUNT_SID, self.AUTH_TOKEN)

    def answer_call(self, call_sid, stream_url, intro_mesaage, voice):
        self.stream_url = stream_url
        self.call_sid = call_sid
        response = VoiceResponse()
        response.say(intro_mesaage, voice=voice)
        start = Start()
        stream_inbound = Stream(url=self.stream_url, track="both_tracks")
        start.append(stream_inbound)
        response.append(start)
        response.pause(self.new_command_timeout)
        return str(response)


    def say_and_wait(self, text, voice):
        response = VoiceResponse()
        response.say(text, voice=voice)
        response.pause(self.new_command_timeout)

        try:
            call = self.client.calls(str(self.call_sid))
            call.update(twiml=str(response))
            self.phone_gpt_object.vosk.outbound_silence_limit = 100
            return True
        except Exception as e:
            print("Error in running command with provided xml: ", str(response), e)
            return None
        
    def send_text_message(self, from_phone_number, to_phone_number, message_body):
        message = self.client.messages.create(
            body=message_body,
            from_=from_phone_number,
            to=to_phone_number
        )
        return message
            
    
        
    
class Openai:
    API_KEY = None

    gpt_role_default = "If you receive an incomplete or unclear grammatical command from me, please make a guess about my intention/command/question and provide assistance accordingly."
    max_tokens = 90
    temperature = 0
    model = "gpt-3.5-turbo"

    messages = []

    def __init__(self, phone_gpt_object, OPENAI_API_KEY):
        self.phone_gpt_object = phone_gpt_object    
        self.API_KEY = OPENAI_API_KEY


    
    def get_gpt_response(self, user_msg, gpt_role):
        openai.api_key = self.API_KEY
        if self.messages == []:
            self.messages = [{"role": "system", "content": gpt_role}]
        self.messages.append({"role": "user", "content": user_msg})
        completion = openai.ChatCompletion.create(
        model=self.model,
        max_tokens=self.max_tokens,
        temperature=self.temperature,
        messages = self.messages
        )
        self.messages.append({"role": "assistant", "content": completion.choices[0].message.content})
        print('\nGPT input:', completion.choices[0].message.content, '\n')
        return completion.choices[0].message.content

class Vosk:
    MODEL_PATH = None
    model = None
    continue_transcribing = True
    outbound_silence_limit = 5000

    silence_time_out = 2
    first_call = True

    accepted_input = ""
    silence_start_time = None
    
    def __init__(self, phone_gpt_object, VOSK_MODEL_PATH):
        self.phone_gpt_object = phone_gpt_object
        self.MODEL_PATH = VOSK_MODEL_PATH
        self.model = vosk.Model(self.MODEL_PATH)
        self.rec = vosk.KaldiRecognizer(self.model, 16000)

    def transcribe_audio_stream(self, ws_data_chunk):
        """Receive and transcribe audio stream with vosk."""
        if True:
            packet = json.loads(ws_data_chunk)
            if packet['event'] == 'start':
                print('\nStreaming is starting')
            elif packet['event'] == 'stop':
                print('\nStreaming has stopped')
            elif (packet['event'] == 'media'):
                if self.continue_transcribing == False:
                    if packet['media']['track'] == 'outbound':
                        self.outbound_silence_limit += 1
                    else:
                        self.outbound_silence_limit -= 1
                    
                    if self.outbound_silence_limit < 0:
                        self.continue_transcribing = True
                        self.outbound_silence_limit = 5000
                    else:
                        return None
                
                audio = base64.b64decode(packet['media']['payload'])
                audio = audioop.ulaw2lin(audio, 2)
                audio = audioop.ratecv(audio, 2, 1, 8000, 16000, None)[0]
            
                if self.rec.AcceptWaveform(audio):
                    r = json.loads(self.rec.Result())                  
                    self.silence_start_time = time.time()
                    self.accepted_input += r['text']
                    print('\x1b[0K' + r['text'] + ' ', end='', flush=True)
                else:
                    if self.silence_start_time is not None:
                        if self.accepted_input.replace(" ","") == "":
                            self.silence_start_time = time.time()
                        if time.time() - self.silence_start_time > self.silence_time_out:
                            self.continue_transcribing = False
                            print('\nUser input:', self.accepted_input)
                            threading.Thread(target=self.phone_gpt_object.on_new_user_input, args=(self.accepted_input,)).start()
                            self.accepted_input = ""
                            return None
                    else:
                        pass
                    r = json.loads(self.rec.PartialResult())
                    print('\x1b[0K' + r['partial'] + '\x08' * len(r['partial']), end='', flush=True)





class PhoneGPT:

        
    def __init__(self, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, OPENAI_API_KEY, VOSK_MODEL_PATH, ON_NEW_MSG_FUNC=None):
        self.twilio = Twilio(self, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        self.openai = Openai(self, OPENAI_API_KEY)
        self.vosk = Vosk(self, VOSK_MODEL_PATH)
        if ON_NEW_MSG_FUNC is not None:
            self.on_new_user_input = ON_NEW_MSG_FUNC

    def on_new_user_input(self, new_user_msg):
            response = self.get_gpt_response(new_user_msg)
            self.say_and_wait(response)

    def answer_call(self, call_sid, stream_url, intro_mesaage='Hi there! How can I help you today?', voice='Google.en-US-Standard-J'):
        return self.twilio.answer_call(call_sid, stream_url, intro_mesaage, voice)

    def say_and_wait(self, text = '', voice='Polly.Salli-Neural'):
        self.twilio.say_and_wait(text, voice)

    def send_text_message(self, from_number=None, to=None, message='empty message.'):
        if from_number is None:
            from_number = self.twilio.client.incoming_phone_numbers.list()[0].phone_number
        if to is None:
            to = self.twilio.client.incoming_phone_numbers.list()[0].phone_number
        return self.twilio.send_text_message(from_number, to, message)

    
    def get_gpt_response(self, user_msg = '', gpt_role=Openai.gpt_role_default):
        return self.openai.get_gpt_response(user_msg, gpt_role)
    
    def transcribe_audio_stream(self, ws_data_chunk):
        self.vosk.transcribe_audio_stream(ws_data_chunk)


