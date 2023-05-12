# 명령어 추가 리스트
msg_input = [] # 추가할 명령어
msg_result = [] # 결과값 
aiToken = 3 # 사용회수

# openAi api_key 가져오기, 질문 입력 및 답변 출력
import openai
# msg에는 웹에서 입력한 value 값 전달
def openAi(msg):
    key1 = "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$" #key값
    openai.api_key = key1
    # {"role":"user", "content":msg}) => 답변, 
    msg_input.append( {"role":"user", "content":msg})

    # 답변 생성, model값 변경으로 다른 모델 사용가능
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=msg_input
    )
    # 답변, 답변에 따라 [1],[2]...까지 수 증가
    answers=response.choices[0].message.content.split("\n\n")
    #answers=response.choices[0].message.content
    print(answers)
    return answers


# 기본 명령어 추가 => """내용""""
# system => 시스템의 기본적인 역할 부여
# assistant => AI가 모르는 내용 보조
def basicAssistant():
    msg_input.append(
        {"role":"system","content":"""너는 최고의 코디네이터고 나에게 옷을 추천해주는 사람이야"""})
    msg_input.append(
        {"role":"assistant","content":"""메이드처럼 나에게 답해줘"""})


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


#============================ flask 실행============================
from flask import Flask, render_template, request
app = Flask(__name__)

#  index페이지, 기본 페이지
@app.route('/')
def home():
    global aiToken #변수 선언
    aiToken = 3 # Token 재설정
    msg_input.clear() # Chat 명령어 초기화
    basicAssistant() # 기본 assistant 추가
    weatherAssistant() # 날씨 assistant 추가
    print(msg_input)
    return render_template('index.html')

# male페이지
@app.route('/male')
def malePage():
    # chat 명령어 추가
    msg_result.clear() # Chat 결과 초기화
    msg_input.append(
        {"role":"assistant","content":"""남자 옷을 추천해줘"""})
    print(msg_input)
    return render_template('male.html')

# female페이지 
@app.route('/female')
def femalePage():
    # chat 명령어 추가
    msg_result.clear() # Chat 결과 초기화
    msg_input.append(
        {"role":"assistant","content":"""여자 옷을 추천해줘"""})
    print(msg_input)
    return render_template('female.html')

# result 페이지
@app.route('/result')
def resultPage():
    global aiToken # token 개수 설정
    aiToken=aiToken-1 # 사용시 하나씩 줄어듬
    
    userQuestion = request.args.get("userQuestion")
    aiResult = openAi(userQuestion) # 답변
    msg_result.append(aiResult) # 답변 리스트 저장
    print(msg_result)
    print(aiToken)
    return render_template('result.html',result=msg_result, token=aiToken)

if __name__ == '__main__':
    app.run('0.0.0.0',port=5002, debug=True)

# ImportError: cannot import name 'EVENT_TYPE_OPENED' from 'watchdog.events'
# -> watchdog.events를 최신으로 업데이트 한다 : pip install --upgrade watchdog
