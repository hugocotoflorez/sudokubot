"""
Sudoku solver v1  
 Hugo Coto Florez 
 Backtracking algorithm  
 Playing on sudoku-online.org 
  
 implementar recursion dividida en hilos 
 """ 
 
from webdriver_manager.chrome import ChromeDriverManager 
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By 
from multiprocessing.pool import ThreadPool 
from selenium import webdriver  
from time import perf_counter 
import numpy as np 
import os 


#MAIN METHOD
def main(): 
    
    def invconv(x,y): 
        '''change the 2d(9x9) index to the
        same in the 1d(81) matrix'''
        return x*9 + y 
        
    def conv(i): 
        '''opposite of invconv'''
        return i//(9), i%9 
    
    #WEBDRIVER DATA 
    path = '.\\chromedriver.exe' if 'chromedriver.exe' in os.listdir() else ChromeDriverManager().install() 
    options = webdriver.ChromeOptions() 

    #SET DRIVER
    driver = webdriver.Chrome(service=Service(path),options=options) 
    
    def get_board(): 
        '''Returns a 1d numpy array
        0: empty cell
        1-9: default number'''
        board_arr = np.zeros(shape=(81),dtype=np.int8) 
        def set_element(i,elem): 
            '''Change the default 0 to a int(0-9)'''
            if t:=elem.text: 
                board_arr[i] = int(t) 
        
        #set every cell in a multithread function
        with ThreadPool() as pool: 
            pool.starmap(set_element,[(i,elem) for i,elem in enumerate(driver.find_elements(By.XPATH,'/html/body/div[5]/div[1]/div[5]/div[1]/div/div[1]/div[1]/div[1]/div[1]/div[3]/table/tbody/tr/td'))]) 
        
        #returns the board  
        return board_arr 
    

            
    def solve(n=0): 
        ''':Returns: None if board is not possible to solve
        array - solved board
        n is the last no default number, used to avoid over looping
        '''
        for k in range(n,81): 
            if board[k]: continue   
            else: 
                i,j = conv(k) 
                #Predetermimadamente todos los numeros pueden ir en cada celda
                probs = [x for x in range(1,10)] 
                
                for a in range(9): 
                    #fila: elimina los números que no pueden ir en la celda
                    if board[invconv(i,a)] in probs: 
                        probs.remove(board[invconv(i,a)]) 
                    #columna: elimina los numeros que no pueden ir en la celda
                    if board[invconv(a,j)] in probs: 
                        probs.remove(board[invconv(a,j)]) 
                #cuadrante: elimina los numeros que no pueden ir en la celda
                u = i//3*3 
                t = j//3*3 
                for a in range(3): 
                    for b in range(3): 
                        di = a+u 
                        dj = b+t 
                        if board[invconv(di,dj)] in probs: 
                            probs.remove(board[invconv(di,dj)]) 

                #Si en una celda no puede ir ningun número el 
                #sudoku no se puede resolver con los datos dados            
                if not probs: return None 
                else: 
                    #llamada recursiva tomando como verdadero cada 
                    #dato posible en ests celda
                    for p in probs: 
                        #para cada posible número asumimos como verdadero
                        #que el tablero en esta celda es ese numero
                        board[k] = p 
                        #se trata de resolver el tablero con el numero asumido
                        s=solve(n=k) 
                        if type(s) != type(None): 
                            #s retorna None o una numpy array, por lo que
                            #s(NpArray) == None da error
                            #all(s(None)) tambien devuelve un error
                            #por lo que la condición compara tipos, devolviendo
                            #verdadero cuando retorne una array, y retornandola
                            return s 
                        
                    
                    # si no se pudo completar con ningun posible numero,
                    # el tablero en esta celda pasa a default y
                    # se retorna None
                    board[k] = 0 
                    return None 
                
        if all(board): 
            #si todas las casillas son distintas de cero
            #el sudoku esta resulto
            return board 
        else: 
            #si hay ceros no esta resulto
            return None 
            
        #posiblemente siempre que llegue al if el 
        #sudoku siempre va a estar resuelto por lo 
        #que se podria eliminar la condición 

            
    def printarr(arr): 
        '''Prints the 2d array'''
        print('-'*2*9) 
        print('\n'.join([' '.join([str(a) for a in arr[b*9:b*9+9]]).replace('0',' ') for b in range(9)]))      
        print('-'*2*9) 
        
    def send_solution(): 
        '''Set the number in each cell, from the 
        local matrix to the online board 
        (!): after this is needed to call "click_cerrar()""'''
        n=0 
        for i,elem in enumerate(driver.find_elements(By.XPATH,'/html/body/div[5]/div[1]/div[5]/div[1]/div/div[1]/div[1]/div[1]/div[1]/div[3]/table/tbody/tr/td/div')): 
            elem.send_keys(str(board[i])+Keys.RIGHT) 
            n+=1 
            if n == 9: 
                elem.send_keys(Keys.LEFT*9+Keys.DOWN)  
                n=0 
                
    def click_acepto(): 
        '''Close the "aceptar coockies" subwindow'''
        try: 
            driver.find_element(By.XPATH,'//*[@id="qc-cmp2-ui"]/div[2]/div/button[2]').click() 
        except Exception as e: 
            print(f"Button 'acepto' not enabled. [{e}]") 
            
    def click_cerrar(): 
        '''Close the message after complete a sudoku'''
        try: 
            driver.find_element(By.XPATH,'//*[@id="mimodal"]/button').click() 
        except Exception as e: 
            print(f"Button 'close' not enabled. [{e}]") 
            
    def set_board_by_number(n:int): 
        '''Select a sudoku by Id'''
        driver.find_element(By.XPATH,'//*[@id="input_numero_sudoku"]').send_keys((Keys.BACK_SPACE)*len(str(n-1))+str(n)) 
        driver.find_element(By.XPATH,'//*[@id="tablero"]/div[1]/div[2]/div/div[1]/div/div[2]/div[1]/div[2]/div').click() 
        
    def set_board_random(): 
        '''Set a new random board'''
        driver.find_element(By.XPATH,'//*[@id="tablero"]/div[1]/div[1]/div[1]/div[2]/div/div[1]/div').click() 
        
    def save_solution(filename,n='',time=0): 
        '''Save solution in the file(.txt) -> filename
        n: Id of the sudoku
        time: time to resolve'''
        with open(filename, 'a') as f: 
            f.write(str(n)+'-'*18+f'{time if time else ""}'+'\n'+('\n'.join([' '.join([str(a) for a in board[b*9:b*9+9]]).replace('0',' ') for b in range(9)]))+'\n') 
    
    
    #GAME OPTIONS 
    reference = f'https://www.sudoku-online.org/'  
    driver.get(reference) 
    click_acepto()        
    #n:int=1 
    time_arr = [] 

    #while True: #main loop
    for _ in range(10):#used to set the sudokus to resolve 
    
        #set_board_by_number(n) 
        t1 = perf_counter() 
        
        #board is called globally, so it changes in site
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
        
    print(f'[>]: Total time:\t{sum(time_arr)} - {time_arr}') 
    print(f'[>]: Average:   \t{sum(time_arr)/20}') 
    print(f'[>]: Min time:  \t{min(time_arr)}') 
    print(f'[>]: Max time:  \t{max(time_arr)}') 
    
    
if __name__ == '__main__':  
    main()
