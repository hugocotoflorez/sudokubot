"""
Sudoku solver v1 
Hugo Coto Florez
Backtracking algorithm 
Playing on sudoku-online.org

implementar recursion dividida en hilos
"""
#################################### modules #########################
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from multiprocessing.pool import ThreadPool
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import perf_counter
import numpy as np
import os

VERBOSE = True

############################ MAIN METHOD ###########################
def main():
    
    def invconv(x,y):
        return x*9 + y
          
    def conv(i):
        return i//(9), i%9
    
    ######################## WEBDRIVER DATA ########################
    path = '.\\chromedriver.exe' if 'chromedriver.exe' in os.listdir() else ChromeDriverManager().install()
    options = webdriver.ChromeOptions()

    ######################### SET DRIVER #############################
    driver = webdriver.Chrome(service=Service(path),options=options)
    
    def get_board():
        board_arr = np.zeros(shape=(81),dtype=np.int8)
        def set_element(i,elem):
            if t:=elem.text:
                board_arr[i] = int(t)
            else:
                board_arr[i] = 0
        
        with ThreadPool() as pool:
            pool.starmap(set_element,[(i,elem) for i,elem in enumerate(driver.find_elements(By.XPATH,'/html/body/div[5]/div[1]/div[5]/div[1]/div/div[1]/div[1]/div[1]/div[1]/div[3]/table/tbody/tr/td'))])
          
        return board_arr
    

            
    def solve(n=0):

        for k in range(n,81):
            if board[k]: continue  
            else:
                i,j = conv(k)
                probs = [x for x in range(1,10)]
                for a in range(9):
                    #fila
                    if board[invconv(i,a)] in probs:
                        probs.remove(board[invconv(i,a)])
                    #columna
                    if board[invconv(a,j)] in probs:
                        probs.remove(board[invconv(a,j)])
                #cuadrante
                u = i//3*3
                t = j//3*3
                for a in range(3):
                    for b in range(3):
                        di = a+u
                        dj = b+t
                        if board[invconv(di,dj)] in probs:
                            probs.remove(board[invconv(di,dj)])

                            
                if not probs: return None
                else:
                    for p in probs:
                        board[k] = p
                        s=solve(n=k)
                        if type(s) != type(None):
                            return s
                    
                    board[k] = 0
                    return None
                
        if all(board):
            return board
        else:
            return None

             
    def printarr(arr):
        print('-'*2*9)
        print('\n'.join([' '.join([str(a) for a in arr[b*9:b*9+9]]).replace('0',' ') for b in range(9)]))     
        print('-'*2*9)
        
    def send_solution():
        n=0
        for i,elem in enumerate(driver.find_elements(By.XPATH,'/html/body/div[5]/div[1]/div[5]/div[1]/div/div[1]/div[1]/div[1]/div[1]/div[3]/table/tbody/tr/td/div')):
            elem.send_keys(str(board[i])+Keys.RIGHT)
            n+=1
            if n == 9:
                elem.send_keys(Keys.LEFT*9+Keys.DOWN) 
                n=0
                
    def click_acepto():
        try:
            driver.find_element(By.XPATH,'//*[@id="qc-cmp2-ui"]/div[2]/div/button[2]').click()
        except Exception as e:
            print(f"Button 'acepto' not enabled. [{e}]")
            
    def click_cerrar():
        try:
            driver.find_element(By.XPATH,'//*[@id="mimodal"]/button').click()
        except Exception as e:
            print(f"Button 'close' not enabled. [{e}]")
            
    def set_board_by_number(n:int):
        driver.find_element(By.XPATH,'//*[@id="input_numero_sudoku"]').send_keys((Keys.BACK_SPACE)*len(str(n-1))+str(n))
        driver.find_element(By.XPATH,'//*[@id="tablero"]/div[1]/div[2]/div/div[1]/div/div[2]/div[1]/div[2]/div').click()
        
    def set_board_random():
        driver.find_element(By.XPATH,'//*[@id="tablero"]/div[1]/div[1]/div[1]/div[2]/div/div[1]/div').click()
        
    def save_solution(filename,n='',time=0):
        with open(filename, 'a') as f:
            f.write(str(n)+'-'*18+f'{time if time else ""}'+'\n'+('\n'.join([' '.join([str(a) for a in board[b*9:b*9+9]]).replace('0',' ') for b in range(9)]))+'\n')
     
     
    ################### GAME OPTIONS ###########################
    reference = f'https://www.sudoku-online.org/' 
    driver.get(reference)
    click_acepto()       
    #n:int=1
    time_arr = []

    for _ in range(10):#main loop 
        #set_board_by_number(n)
        t1 = perf_counter()
        board = get_board()

        solve()
        printarr(board)
        #send_solution()
        total_time = perf_counter()-t1
        time_arr.append(total_time)
        #save_solution("sudoku_solutions.txt",time=total_time)
        #click_cerrar()
        #n+=1
        set_board_random()
        
    print(f'[>]: Total time:\t{sum(time_arr)}')
    print(f'[>]: Average:   \t{sum(time_arr)/20}')
    print(f'[>]: Min time:  \t{min(time_arr)}')
    print(f'[>]: Max time:  \t{max(time_arr)}')
    

        
        
    
     
if __name__ == '__main__': 
    main()
        