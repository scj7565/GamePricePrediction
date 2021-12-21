import glob, csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sklearn.svm import SVR
import tkinter

def read_data(filename):
    files = glob.glob(filename)
    all_data = []
    for file in files:
        with open(file, 'r') as f:
            csv_reader = csv.reader(f)
            data = []
            for line in csv_reader:
                if line and not line[0].strip().startswith('#'):
                    data.append([float(val) for val in line])
            all_data = all_data + data
    return all_data
    
if __name__ == '__main__':
    support_box = read_data('support_box.csv')

    # 가격 list 제작
    # 모든 생기는 10000 기준
    # 영지 1000 당 1.2, 구매 1000 당 1.4
    living_gold = [np.ceil(row[1]) * 5 + np.ceil(row[2]) * 25 + np.ceil(row[3]) * 15 for row in support_box]    # 생기 판매 골드
    living_gold = np.array(living_gold)
    living_gold = living_gold.astype('int')
    making_gold = [(np.ceil(row[0]) * 9 - 14) * 12 for row in support_box]  # 영지 제작 골드
    making_gold = np.array(making_gold)
    making_gold = making_gold.astype('int')
    buying_gold = [(np.ceil(row[0]) * 3 - (np.ceil(row[4]) * 2)) * 14 for row in support_box]   # 재료 구입 제작 골드
    buying_gold = np.array(buying_gold)
    buying_gold = buying_gold.astype('int')
    
    living_making = np.array(making_gold - living_gold) # 영지 제작 - 생기 판매
    buying_making = np.array(living_gold - buying_gold) # 영지 제작 - 재료 구입
    
    days = []
    i = 1
    for i in range(len(support_box)):
        days.append([int(i + 1)])
        i = i + 1
    
    # model 만들기
    living_model = SVR(kernel = 'rbf', C=1000, gamma = 0.2)
    living_model.fit(days, living_making)
    living_pre = np.ceil(living_model.predict(days))
    living_pre = living_pre.astype('int')
    buying_model = SVR(kernel = 'rbf', C=1000, gamma = 0.2)
    buying_model.fit(days, buying_making)
    buying_pre = np.ceil(buying_model.predict(days))
    buying_pre = buying_pre.astype('int')
      
    # 내일 가격 예측
    pre_day = [[len(days) + 1]]
    pre_living = int(np.ceil(living_model.predict(pre_day)))
    pre_buying = int(np.ceil(buying_model.predict(pre_day)))
    
    # GUI
    window = tkinter.Tk()
    window.title("Game Price Prediction")
    window.geometry("910x500+100+100")
    window.resizable(False, False)
    title_label = tkinter.Label(window, text = "영지 생활 효율 계산기", font = 30, height = 2)
    title_label.grid(row = 0, column = 0, columnspan = 5)
    entry_info = tkinter.Label(window, text = "신호탄,투박한 버섯,싱싱한 버섯,화려한 버섯,자연산 진주 의 가격을 띄어쓰기 없이 ,로 구분하여 입력해주세요.")
    entry_info.grid(row = 1, column = 0, sticky = 'w')
    def enter_button():
        global temp_string
        temp_string = entry_txt.get()
        f = open('support_box.csv', 'a')
        f.write(temp_string)
        f.write('\n')
        f.close()
        tkinter.messagebox.showinfo("저장", "성공적으로 저장되었습니다.\n변경된 정보를 확인하기 위해 재시작해주세요.")
    temp_string = ''
    entry_txt = tkinter.Entry(window)
    entry_txt.grid(row = 2, column = 0, columnspan = 4, sticky = 'ew')
    entry_button = tkinter.Button(window, text='입력', command = enter_button)
    entry_button.grid(row = 2, column = 4, sticky = 'ew')
    blank1 = tkinter.Label(window)
    blank1.grid(row = 3, column = 0)
    info_text = tkinter.Label(window, text = "모든 값은 생활의 기운 1000기준입니다.")
    info_text.grid(row = 4, column = 0, columnspan = 5)
    blank2 = tkinter.Label(window)
    blank2.grid(row = 6, column = 0)
    pre_text1 = tkinter.Label(window, text =(f"영지 제작시 오늘 이득 : {living_making[-1]}골드"), font = 15)
    pre_text1.grid(row = 7, column = 0, sticky = 'w')
    pre_text2 = tkinter.Label(window, text =(f"영지 제작시 내일 예상 이득 : {pre_living}골드"), font = 15)
    pre_text2.grid(row = 7, column = 1, sticky = 'w')
    pre_text3 = tkinter.Label(window, text =(f"구매 제작시 오늘 이득 : {buying_making[-1]}골드"), font = 15)
    pre_text3.grid(row = 8, column = 0, sticky = 'w')
    pre_text4 = tkinter.Label(window, text =(f"구매 제작시 내일 예상 이득 : {pre_buying}골드"), font = 15)
    pre_text4.grid(row = 8, column = 1, sticky = 'w')

    # plot 폰트 설정
    from matplotlib import font_manager, rc
    font_path = "C:/Windows/Fonts/NGULIM.TTF"
    font = font_manager.FontProperties(fname = font_path).get_name()
    rc('font', family = font)
    
    # plot 설정
    fig = plt.figure(figsize=(7, 3), dpi = 100)
    graph1 = fig.add_subplot(1,2,1)
    graph1.plot(days, living_making, 'r-')
    ax = plt.gca()
    ax.get_xaxis().set_visible(False)
    graph1.set_title('영지 제작')
    graph1.grid()
    graph2 = fig.add_subplot(1,2,2)
    graph2.plot(days, buying_making, 'r-')
    ax = plt.gca()
    ax.get_xaxis().set_visible(False)
    graph2.set_title('구매 제작')
    graph2.grid()
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()
    canvas.get_tk_widget().grid(row = 5, column = 0, columnspan = 5)

    window.mainloop()