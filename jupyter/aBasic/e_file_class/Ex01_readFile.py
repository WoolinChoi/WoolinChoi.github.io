"""
@ 파일 읽고 쓰기
    - 파일을 읽고 쓰기 전에 파일을 열어야 한다
    - fileObj = open ( filename, mode )
            mode 첫번째 글자 - 작업 표시
            r(read)  : 파일 읽기
            w(write) : 파일 쓰기 ( 파일이 없으면 생성하고 파일이 있으면 덮어쓴다 )
            x(write) : 파일 쓰기 ( 파일이 없을 때만 생성하고 쓴다 )
            a(append) : 파일 추가 ( 파일이 있으면 파일의 끝에서부터 추가하여 쓴다 )

            mode 두번째 글자 - 파일 타입
            t : 텍스트(text) 타입 ( 기본값 )
            b : 이진(binary) 타입
            두번째 글자가 없으면 텍스트 타입이다.

            encoding='utf-8' : 한글

    - 파일을 열고 사용 후에는 반드시 닫아야 한다
    #### 파일을 자동으로 닫아주는 with 구문을 사용 ####
"""
f = open("./data/temp.xml", "rt", encoding='utf-8')
while True:
    line = f.readline()
    if not line : break
    print(line, end="")
f.close()

try:
    f2 = open("./data/temp2.xml", "rt", encoding='utf-8')
    while True:
        line = f2.readline()
        if not line: break
        print(line, end="")
    f2.close()
except Exception as e:
    print("예외발생:", e)
else:
    print("\n 정상종료")

try:
    with open("./data/temp3.xml", "rt", encoding='utf-8') as f3:
        while True:
            line = f3.readline()
            if not line: break
            print(line, end="")
except FileNotFoundError as e:
    print("예외발생:", e)
else:
    print("\n 정상종료")

try:
    with open("./data/temp2.xml", "r", encoding='utf-8') as f4:
        content = f4.read()
        words = content.split()
        num = len(words)
except FileNotFoundError as e:
    pass
else:
    print("파일의 총 단어수:", num)