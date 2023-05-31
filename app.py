#! pip install SpeechRecognition
#! pip install pyaudio
#! pip install gtts

import os
# 명령어 추가 리스트
msg_input = [] # 명령어 리스트
dall2_input = [] # dall2 명령어
msg_result = [] # 결과값 리스트
aiToken = 3 # 사용회수
audioList =[""] # 음성변환 리스트
voiceAudio = "" # 음성인식 값 저장


# ======================openai def======================
# openAi api_key 가져오기, 질문 입력 및 답변 출력
import openai

# msg에는 웹에서 입력한 value 값 전달
def openAi(msg):
    key1 = "***********************************************************" #key값
    openai.api_key = key1
    # {"role":"user", "content":msg}) => 답변, 
    msg_input.append( {"role":"user", "content":msg})

    # 답변 생성, model값 변경으로 다른 모델 사용가능
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=msg_input
    )
    # 답변, 답변에 따라 [1],[2]...까지 수 증가
    answers=''.join(response.choices[0].message.content.split("\n"))
    return answers

# ==================basicassistant def==================
# 기본 명령어 추가 => """내용""""
# system => 시스템의 기본적인 역할 부여
# assistant => AI가 모르는 내용 보조
def basicAssistant():
    msg_input.append(
        {"role":"system","content":"너는 최고의 코디네이터며, 나에게 옷을 추천해주는 사람이야"})
    msg_input.append(
        {"role":"assistant","content":"메이드처럼 나에게 대답해주고, 나와의 대화는 200글자 안으로 대답해줘"})


# ===============Beautifulsoup를 이용한 날씨 정보 추가===============
# basicAssitant() 함수에 추가 가능, 현재는 구분을 위해 따로 작성
# url의 해당정보 가져오기
from urllib.request import urlopen
# beautifulSoup 이용하기, 정보를 쉽게 가져오도록 beautiful soup 이용
from bs4 import BeautifulSoup
def weatherAssistant():
    url = "https://weather.naver.com/" # 네이버 날씨에서 크롤링
    page = urlopen(url)
    soup = BeautifulSoup(page,'lxml')
    # 날씨
    weath = soup.find("span",class_="weather").text
    # 온도
    temp = soup.find("strong",class_="current").text
    now_temp = temp[1:-1]
    weather = "오늘 날씨는 "+weath+", "+now_temp
    # chat에 assistant 추가
    msg_input.append({"role":"assistant","content":weather})


# ===============speech_recognition을 통한 음성 인식===============
# 다른 형태의 음성 인식 저장 가능
import speech_recognition as sr
def audioRecognize():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say Something")
        speech = r.listen(source)
    try:
        global voiceAudio 
        voiceAudio = r.recognize_google(speech, language="ko-KR")
        print("Your speech thinks like\n " + voiceAudio)
    except sr.UnknownValueError:
        voiceAudio = "음성이 없습니다"
        print("Your speech can not understand")
    except sr.RequestError as e:
        print("Request Error!; {0}".format(e))
    return voiceAudio

# ===============gtts를 통한 음성 출력===============
from gtts import gTTS
def audioOutput(answersList, token): # answerList로 리스트 정보를 변수로 받아옴
    answerStr = ''.join(str(s) for s in answersList) # 리스트를 string 형식으로 변환
    tts = gTTS(text=answerStr, lang="ko")
    #여성 ko-KR-Neural2-A,ko-KR-Neural2-B 남성 :ko-KR-Neural2-C
    #여성 음성은 유료$$$
    tts.voice = "ko-KR-Neural2-C"
    tts.save("static\output%d.mp3"%token)

# ===============chat을 통한 dall-2_prompt 생성===============
def dall2_chat(resultList): # string type 추가
        aiResult = ''.join(str(s) for s in resultList)
        # 달리 prompt를 위한 chatgpt
        dall2_input = []
        urlList = []
        dall2_input.append({"role":"system","content":"Image generator through words"})
        dall2_input.append({"role":"assistant", "content":aiResult})
        dall2_input.append({"role":"user","content":"list the words related to the costume in English using , "})
        response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=dall2_input
                )
        answers=response.choices[0].message.content
        ### dalle 그림 생성
        dall_e_response = openai.Image.create(
                prompt = "Mannequin wearing clothes"+answers,
                n=3,# n=3
                size = "1024x1024"
                )
        image_url1 = dall_e_response['data'][0]['url']
        image_url2 = dall_e_response['data'][1]['url']
        image_url3 = dall_e_response['data'][2]['url']
        urlList.append(image_url1)
        urlList.append(image_url2)
        urlList.append(image_url3)
        return urlList

#============================ flask 실행============================
from flask import Flask, render_template, request
app = Flask(__name__)

#  index페이지, 기본 페이지
@app.route('/') # 루트 설정
def home():
    global aiToken #변수 선언
    aiToken = 3 # Token 재설정
    global voiceAudio
    voiceAudio = ""
    msg_input.clear() # Chat 명령어 초기화
    basicAssistant() # 기본 assistant 추가
    weatherAssistant() # 날씨 assistant 추가
    return render_template('index.html')

# male페이지
@app.route('/male')
def malePage():
    # chat 명령어 추가
    msg_result.clear() # Chat 결과 초기화
    msg_input.append(
        {"role":"assistant","content":"남자 옷을 추천해줘"})
    print(msg_input)
    return render_template('male.html')

# female페이지 
@app.route('/female')
def femalePage():
    # chat 명령어 추가
    msg_result.clear() # Chat 결과 초기화
    msg_input.append(
        {"role":"assistant","content":"여자 옷을 추천해줘"})
    print(msg_input)
    return render_template('female.html')

# result 페이지
@app.route('/result')
def resultPage():
    global aiToken # token 개수 설정
    aiToken=aiToken-1 # 사용시 하나씩 줄어듬
    global audioList
    
    print(msg_input)
    ### openai 질문
    userQuestion = request.args.get("userQuestion")
    aiResult = openAi(userQuestion) # 답변
    msg_result.append(aiResult) # 답변 리스트 저장

    ### dall2 이용
    urlList = dall2_chat(msg_result)
    
    # 음성파일 생성
    audioList[0] = msg_result[2-aiToken] # 현재 분기에서의 음성 파일 생성
    audioOutput(audioList,aiToken) # 현재 상황에서 출력된 요소만 출력

    # html 페이지로 넘기는 값
    return render_template('result.html',result=msg_result, token=aiToken, urlList=urlList)

@app.route('/resultVoice')
def resultVoicePage():
    global aiToken # token 개수 설정
    aiToken=aiToken-1 # 사용시 하나씩 줄어듬
    global audioList
    
    print(msg_input)
    ### openai 질문
    #userQuestion = request.args.get("userQuestion")
    userQuestion = audioRecognize()
    aiResult = openAi(userQuestion) # 답변
    msg_result.append(aiResult) # 답변 리스트 저장

    ### dall2 이용
    urlList = dall2_chat(msg_result)
    
    # 음성파일 생성
    audioList[0] = msg_result[2-aiToken] # 현재 분기에서의 음성 파일 생성
    audioOutput(audioList,aiToken) # 현재 상황에서 출력된 요소만 출력

    # html 페이지로 넘기는 값
    return render_template('result.html',result=msg_result, token=aiToken, urlList=urlList)

if __name__ == '__main__':
    app.run('0.0.0.0',port=5002, debug=True)

# ImportError: cannot import name 'EVENT_TYPE_OPENED' from 'watchdog.events'
# -> watchdog.events를 최신으로 업데이트 한다 : pip install --upgrade watchdog
