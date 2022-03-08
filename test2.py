import random #引入随机库


h_range=[]
b_range=[]
ha_range=[]
bf_range=[]
tf_range=[]
tw_range=[]
n_range=[]
d_range=[25,28,32]
nsv_range=[2,4]
dsv_range=[8,10,12]
s_range=[100,150,200]

L = 17.500           #跨度
g1 = 100            #附加恒荷载
q = 200             #活荷载




for i in range(int(L*1000/10/50), int(L*1000/5/50)):
    h_range.append(i*50)  




error_message=[]


def create_answer(n): #创建初始解集
    result=[]

    for i in range(n):
        h=random.sample(h_range,1)[0]

        for i in range(int(h/3/50), int(h/2/50)):
            b_range.append(i*50)  

        b=random.sample(b_range,1)[0]

        for i in range(int(h/3/50), int((h-200)/50)):
            ha_range.append(i*50) 
        for i in range(int(b/3/50), int((b-200)/50)):
            bf_range.append(i*50) 



        ha=random.sample(ha_range,1)[0]
        bf=random.sample(bf_range,1)[0]

        for i in range(max(int(bf/2/19/2),3),18):
            tf_range.append(i*2) 
        tf=random.sample(tf_range,1)[0]
        for i in range(max(int(ha/2/91/2),3,int((0.04*b*h-2*tf*bf)/(2*tf*bf))),18):
            tw_range.append(i*2) 


        tw=random.sample(tw_range,1)[0]

        result.append([h,b,ha,bf,tf,tw])


    return result



def answer_calcu(new_answer):     #验算
    h=new_answer[0]
    b=new_answer[1]
    ha=new_answer[2]
    bf=new_answer[3]
    tf=new_answer[4]
    tw=new_answer[5]


    value=0


    g2 = b*h*gamma_c/1000/1000
    Sd=gamma_G*(g1+g2)+gamma_Q*q  #荷载组合
    Sdq=gamma_G*(g1+g2)+gamma_Q*q*psi_q
    M=int(Sd*L**2/8)
    Vb=int(Sd*L)
    Mq=int(Sdq*L**2/8)



    #构造演算
    if 0.5*(h-ha)<100 or 0.5*(b-bf)<100 or b-bf<b/3:
        value+=9999999999
        error_message.append("构造不满足1")



    hw=ha-2*tf
    Aa=2*tf*bf+hw*tw
    if Aa/(b*h)<0.04:
        value+=9999999999
        error_message.append("含钢率不满足")


    if (bf-tw)/2/tf>19 or hw/tw>91:
        value+=9999999999
        error_message.append("宽厚比不满足")
    gamma_s=1.05
    I=(bf*ha**3-(bf-tw)*(ha-2*tf))/12
    Wss=I/(ha/2)

    Mby=gamma_s*Wss*fa
    Mbu=M-Mby
    h0=((h-c)+(h-c-s1))/2
    alpha_s=Mbu/(fc*b*h0**2)
    gamma_sc=0.5*(1+(1-2*alpha_s)**0.5)
    As=Mbu/(fy*gamma_sc*h0)
    As_=0.003*b*h
    
    aa=0.5*(h-hw-tf)
    Aaf=tf*bf
    as0=h-h0

    rhos=As/(b*h0)


    if rhos<0.003 or rhos>0.025:
        value+=9999999999
        error_message.append("配筋率不足0.3%")


    #斜截面验算

    

    #裂缝验算

    Mcr=0.235*b*h**2*ftk/1000000

    k=(0.25*h-0.5*tf-aa)/hw
    Aaw=hw*tw
    hof=h-aa
    how=(5*h+2*hw)/8
    sigmasa=Mq*1000000/0.87/(As*(h-as0)+Aaf*hof+k*Aaw*how)
    u=1+(2*bf+2*tf+2*k*hw)*0.7
    Psi=1.1*(1-Mcr/Mq)
    de=4*(As+Aaf+k*Aaw)/u
    rhote=(As+Aaf+k*Aaw)/0.5/b/h
    omegamax=1.9*Psi*sigmasa/Es*(1.9*c+0.08*de/rhote)
    if sigmasa>omega_lim:
        value+=9999999999
        error_message.append("裂缝验算不满足")
    value+=(Aa)/1000000000*5500+(b*h-Aa)/1000000*300
    print("当前",value,error_message[0])
    return value

def error_level(new_answer): #计算解集的误差
    error=[]
    for item in new_answer:

        value=answer_calcu(item) #误差
        error.append(1/value)
    return error

def choice_selected(old_answer):    #遗传、交叉
    result=[]
    error=error_level(old_answer)
    error_one=[item/sum(error) for item in error] #归一化
    for i in range(1,len(error_one)):   #len(error_one):error_one中元素的个数
        error_one[i]+=error_one[i-1]    #叠加化
    for i in range(len(old_answer)//2): #每次从解集中抽出2个解
        temp=[]
        for j in range(2):  #父体和母体
            rand=random.uniform(0,1)    #随机出一个浮点数(0～1之间的小数)
            for k in range(len(error_one)): #遍历error_one[k],把随机数rand对应
                if k==0:
                    if rand<error_one[k]:   #将随机出来的浮点数rand落在归一化后的误差中，将所在区间处对应的解返回到temp中，目的是找到k
                        temp.append(old_answer[k])
                else:
                    if rand>=error_one[k-1] and rand<error_one[k]:
                        temp.append(old_answer[k])
        rand=random.randint(0,5) #每次交换3个数字，一共10个数字
        temp_1=temp[0][:rand]+temp[1][rand:rand+3]+temp[0][rand+3:]
        temp_2=temp[1][:rand]+temp[0][rand:rand+3]+temp[1][rand+3:]
        result.append(temp_1)
        result.append(temp_2)
    return result

def variation(old_answer,pro):  #变异，pro是设定的变异概率
    for i in range(len(old_answer)):

        h=old_answer[i][0]

        for i in range(int(h/3/50), int(h/2/50)):
            b_range.append(i*50)  
        for i in range(int((h-200)/10/50), int((h-200)/5/50)):
            ha_range.append(i*50) 
        b=old_answer[i][1]
        for i in range(int((b-200)/24/50), int((b-200)/12/50)):
            bf_range.append(i*50) 
        bf=old_answer[i][3]
        for i in range(max(int(bf/2/19/2),3),18):
            tf_range.append(i*2)
        ha=old_answer[i][2]
        for i in range(max(int(ha/2/91/2),3),18):
            tw_range.append(i*2) 


        rand=random.uniform(0,1)
        if rand<pro:

            rand_num=random.randint(0,5)

            if rand_num==0:
                old_answer[i]=old_answer[i][:rand_num]+random.sample(b_range,1)+old_answer[i][rand_num+1:]
            elif rand_num==1:
                old_answer[i]=old_answer[i][:rand_num]+random.sample(h_range,1)+old_answer[i][rand_num+1:]
            elif rand_num==2:
                old_answer[i]=old_answer[i][:rand_num]+random.sample(ha_range,1)+old_answer[i][rand_num+1:]
            elif rand_num==3:
                old_answer[i]=old_answer[i][:rand_num]+random.sample(bf_range,1)+old_answer[i][rand_num+1:]
            elif rand_num==4:
                old_answer[i]=old_answer[i][:rand_num]+random.sample(tf_range,1)+old_answer[i][rand_num+1:]
            elif rand_num==5:
                old_answer[i]=old_answer[i][:rand_num]+random.sample(tw_range,1)+old_answer[i][rand_num+1:]

    return old_answer




#自变量X


fc=14.3         #混凝土抗压强度设计值
ft=1.43         #混凝土抗拉强度设计值
ftk=2.01        #混凝土抗拉强度标准值
fa=295          #钢材强度
fy=360          #抗拉纵筋强度
fy_=360         #抗压纵筋强度
fyv=360         #箍筋强度
alpha_1=1       #受压区混凝土压应力影响系数α1
beta_1=0.8      #以受压区混凝土应力图形影响系数β1
beta_c=1        #混凝土强度影响系数
c=50            #保护层厚度
s1=125          #钢筋层净距离
omega_lim=0.2  #控制裂缝宽度
gamma_0=1       #重要性系数     
psi_q=0         #准永久值系数
gamma_c=25      #混凝土容重
gamma_G=1.3     #恒荷载分项系数
gamma_Q=1.5     #活荷载分项系数
Es=200000       #钢筋弹性模量
pi=3.14
gamma_s=1.05






middle_answer=create_answer(1000)
#print(middle_answer)
first_answer=middle_answer[0]
great_answer=[]


for i in range(100): #主程序，循环1000次
    middle_answer=choice_selected(middle_answer)    #选择，交换
    middle_answer=variation(middle_answer,0.4)      #变异
    error=error_level(middle_answer)    #误差评估
    index=error.index(max(error))   #返回误差最小的一组结果所在的位置
    great_answer.append([middle_answer[index],error[index]]) #将该结果放入great_answer中
great_answer.sort(key=lambda x:x[1],reverse=True) #对great_answer进行排序，great_answer[0]就是最优解


print(great_answer[0])




