import MetaTrader5 as mt5
import json
import pandas as pd

from line_ex_forex_next3 import LINE
from buy_sell_ex_forex_next3 import BUY_SELL
from database_ex_forex_next3 import Database


class Pullback:
 
 def __init__(self , symbol_EURUSD , decimal_sambol ):
      
      self.symbol_EURUSD = symbol_EURUSD
      self.decimal_sambol = decimal_sambol

 def __str__(self):
      return f"({self.symbol_EURUSD },{self.decimal_sambol })"


 def pullback_1 (self , tel , status_tel , timestamp_pulback , lot):
     
   telo = '0.0'
   for i in range(self.decimal_sambol - 2):  
      telo = telo + "0"
      
   telo = telo + f"{tel}"  
   telo = float (telo)
#    print("telerance:" , telo) 

   data_all = Database.select_table_All()
   select_all_len = len(data_all)
   if select_all_len > 0:
     #  print("select_all_len:" , select_all_len)
      rec = data_all[select_all_len - 1]
      # print("rec:" , rec)

      for index in range(select_all_len):
                          
     #     print("index:" , index)
         lab = data_all[index]
         candel_num = lab[1]
         type = lab[2]
         point_patern = lab[3]
         timepstamp = lab[19] 
         time_start_search = lab[17]
         status = lab[15]
         chek = lab[16]


         time_start_search = int(time_start_search)
     #     print("lab:" , lab)
     #     print("status:" , status)
     #     print("time_start_search:" , time_start_search)
     #     print("point_patern:" , point_patern)
     #     print("type:" , type)
     #     print("candel_num:" , candel_num)
     #     print("timepstamp:" , timepstamp)


         point_patern = json.loads(point_patern)
         timepstamp = json.loads(timepstamp)
         timepstamp_3 = json.loads(timepstamp[3])

     #     print("timepstamp_3:" , timepstamp_3)

         timepstamp_old = int(timepstamp_3) + 900
     #     print("timepstamp_old:" , timepstamp_old)
         print("Pulback 111111111111111111111111111111111111111111111111111111111111111111111111111111111111")

         if status == "true" and chek == "false":
               

            inputs_candels = mt5.copy_rates_range(self.symbol_EURUSD, mt5.TIMEFRAME_M1, timepstamp_old, timestamp_pulback)
               # print("inputs_candels:" , inputs_candels)

            for candel_recive in inputs_candels:
               # print("candel_recive:" , candel_recive)
          
               point_open = "{:.5f}".format(candel_recive[1])
               point_open = float(point_open)
               # print ("point_open:" , point_open)

               point_close = "{:.5f}".format(candel_recive[4])
               point_close = float(point_close)
               # print ("point_close:" , point_close)
       
               point_high = "{:.5f}".format(candel_recive[2])
               point_high = float(point_high)
               # print ("point_high:" , point_high)
       
               point_low = "{:.5f}".format (candel_recive[3])
               point_low = float(point_low)
               # print ("point_low:" , point_low)
       
               candel_statess = ''
               if point_open > point_close:
                 candel_statess = "red"
               elif point_open < point_close:
                 candel_statess = "green"
               elif point_open == point_close:
                 candel_statess = "doji"  
       
               # print("candel_state:" , candel_statess)
       
               # cal_point = LINE.cal_point_line(1 , timestamp_pulback)
               # print("cal_point:" , cal_point)
               cal_line =  LINE.line_run(candel_num , self.symbol_EURUSD , timestamp_pulback )
               # print("cal_line:" , cal_line)


               telo_add_high = point_high + telo
               telo_sub_high = point_high - telo
               telo_add_high = "{:.5f}".format(telo_add_high)
               telo_sub_high = "{:.5f}".format(telo_sub_high)
               telo_add_high = float(telo_add_high)
               telo_sub_high = float(telo_sub_high)

               telo_add_low = point_low + telo
               telo_sub_low = point_low - telo
               telo_add_low = "{:.5f}".format(telo_add_low)
               telo_sub_low = "{:.5f}".format(telo_sub_low)
               telo_add_low = float(telo_add_low)
               telo_sub_low = float(telo_sub_low)


               # print("telo_add_high:" , telo_add_high)
               # print("telo_sub_high:" , telo_sub_high)

               # print("telo_add_low:" , telo_add_low)
               # print("telo_sub_low:" , telo_sub_low)

               a = 1
               for i in range(self.decimal_sambol + 1):
                     a = a * 10
               
               cal_price_candel = abs( int(point_open * a) - int(point_close * a) )
               cal_price_candel = int (cal_price_candel / 10)
               # print("cal_price_candel:" , cal_price_candel)

               
               for line , gap_point in enumerate(cal_line): 
                     
                     # print("gap:" , gap_point)
                     
                     cal_point = float (gap_point)

                     rec = Database.select_table_One(candel_num)
                     chek = rec[0][16]
                    #  print("chek:" , chek)
                     

                     if (point_close != point_high and candel_statess == "green") or (point_open != point_low and candel_statess == "red"):
                         
                         
                         # print("cal_point:" , cal_point)
                         # print("tel:" , tel)
                         
                         if point_high == cal_point and type == "Two_TOP" and chek == "false":
                                 print("point_high:" , point_high)
                                 print("candel_color:" , candel_statess)
                                 print ("line:" , line + 1)
                                 print("patern: up  11111111111111111111111111111111111111111111")
                                 print("pullback_MMMMMMMMMMM")
                                 time_command = pd.to_datetime( timestamp_pulback , unit='s')
                                 shakhes = LINE.line_shakhes(candel_num , self.symbol_EURUSD , self.decimal_sambol)
                                 status_trade = shakhes[1]
                                 print("status_trade:" , status_trade)
                                 shakhes = int (shakhes[0])
                                 commands = f'{candel_num}' + "_" + f'B' + "_" + f'{line + 1}' + '_' + f'{shakhes}' + "_" + f'{1}'
                                 ticket = 0
                                 execution = 0
                                 if status_trade == True:
                                     print("shakhes: True" )
                                     rec_pos = BUY_SELL.pos_sell(point_high , shakhes , lot , self.symbol_EURUSD , commands)
                                     execution = rec_pos.comment
                                     if execution == 'Request executed':
                                            ticket =  rec_pos.order
                                            print("rec_pos:" , rec_pos)
                                            print("ticket:" , ticket)
                                 command = "(Patern:" + f'{candel_num})' + " _ " + "(Type:" + f'{type})' + " _ " + "(Line:" + f'{line + 1})' + ' _ ' + "(Shakhes:" + f'{shakhes})' + " _ " + "(Pulback:" f'{1})'+ " _ " + "(Point5:" + f'{point_high})' + " _ " + "(Time:" + f'{time_command})' + " _ " + "(High:" + f'{tel})' + " _ " + "(Status_trade:" + f'{status_trade})' + " _ " + "(ticket:" + f'{ticket})' + " _ " + "(execution:" + f'{execution})' + " _ " + "(list_line:" + f'{cal_line})' 
                                 Database.update_table_chek(point_high , timestamp_pulback , command , "true" , ticket , candel_num)     

                         elif telo_add_high == cal_point and cal_price_candel > tel  and type == "Two_TOP" and  status_tel == True and chek == "false":
                                 print("point_high:" , point_high)
                                 print("candel_color:" , candel_statess)
                                 print ("line:" , line + 1)
                                 print("patern: up  22222222222222222222222222222222222222222222") 
                                 print("pullback_MMMMMMMMMMM")

                                 time_command = pd.to_datetime( timestamp_pulback , unit='s')
                                 shakhes = LINE.line_shakhes(candel_num , self.symbol_EURUSD , self.decimal_sambol)
                                 status_trade = shakhes[1]
                                 print("status_trade:" , status_trade)
                                 shakhes = int (shakhes[0])
                                 commands = f'{candel_num}' + "_" + f'B' + "_" + f'{line + 1}' + '_' + f'{shakhes}' + "_" + f'{1}'
                                 ticket = 0
                                 execution = 0
                                 if status_trade == True:
                                     print("shakhes: True" )
                                     rec_pos = BUY_SELL.pos_sell(telo_add_high , shakhes , lot , self.symbol_EURUSD , commands)
                                     execution = rec_pos.comment
                                     if execution == 'Request executed':
                                            ticket =  rec_pos.order
                                            print("rec_pos:" , rec_pos)
                                            print("ticket:" , ticket)
                                 command = "(Patern:" + f'{candel_num})' + " _ " + "(Type:" + f'{type})' + " _ " + "(Line:" + f'{line + 1})' + ' _ ' + "(Shakhes:" + f'{shakhes})' + " _ " + "(Pulback:" f'{1})'+ " _ " + "(Point5:" + f'{telo_add_high})' + " _ " + "(Time:" + f'{time_command})' + " _ " + "(telo_add_high:" + f'{tel})' + " _ " + "(Status_trade:" + f'{status_trade})' + " _ " + "(ticket:" + f'{ticket})' + " _ " + "(execution:" + f'{execution})' + " _ " + "(list_line:" + f'{cal_line})' 
                                 Database.update_table_chek(telo_add_high , timestamp_pulback , command , "true" , ticket , candel_num)     

                         elif telo_sub_high == cal_point and cal_price_candel > tel and type == "Two_TOP" and status_tel == True and chek == "false":
                                 print("point_high:" , point_high)
                                 print("candel_color:" , candel_statess)
                                 print ("line:" , line + 1)
                                 print("patern: up  33333333333333333333333333333333333333333333")   
                                 print("pullback_MMMMMMMMMMM")     
                                 time_command = pd.to_datetime( timestamp_pulback , unit='s')
                                 shakhes = LINE.line_shakhes(candel_num , self.symbol_EURUSD , self.decimal_sambol)
                                 status_trade = shakhes[1]
                                 print("status_trade:" , status_trade)
                                 shakhes = int (shakhes[0])
                                 commands = f'{candel_num}' + "_" + f'B' + "_" + f'{line + 1}' + '_' + f'{shakhes}' + "_" + f'{1}'
                                 ticket = 0
                                 execution = 0
                                 if status_trade == True:
                                     print("shakhes: True" )
                                     rec_pos = BUY_SELL.pos_sell( telo_sub_high , shakhes , lot , self.symbol_EURUSD , commands)
                                     execution = rec_pos.comment
                                     if execution == 'Request executed':
                                            ticket =  rec_pos.order
                                            print("rec_pos:" , rec_pos)
                                            print("ticket:" , ticket)
                                 command = "(Patern:" + f'{candel_num})' + " _ " + "(Type:" + f'{type})' + " _ " + "(Line:" + f'{line + 1})' + ' _ ' + "(Shakhes:" + f'{shakhes})' + " _ " + "(Pulback:" f'{1})'+ " _ " + "(Point5:" + f'{telo_sub_high})' + " _ " + "(Time:" + f'{time_command})' + " _ " + "(telo_sub_high:" + f'{tel})' + " _ " + "(Status_trade:" + f'{status_trade})' + " _ " + "(ticket:" + f'{ticket})' + " _ " + "(execution:" + f'{execution})' + " _ " + "(list_line:" + f'{cal_line})' 
                                 Database.update_table_chek(telo_sub_high , timestamp_pulback , command , "true" , ticket , candel_num)     

                         elif point_low == cal_point and type == "Two_Bottom" and chek == "false":
                                 print("point_low:" , point_low)
                                 print("candel_color:" , candel_statess)
                                 print ("line:" , line + 1)
                                 print("patern: down  11111111111111111111111111111111111111111111")
                                 print("pullback_HHHHHHHHHH")
                                 time_command = pd.to_datetime( timestamp_pulback , unit='s')
                                 shakhes = LINE.line_shakhes(candel_num , self.symbol_EURUSD , self.decimal_sambol)
                                 status_trade = shakhes[1]
                                 print("status_trade:" , status_trade)
                                 shakhes = int (shakhes[0])
                                 print("shakhes:" , shakhes)
                                 commands = f'{candel_num}' + "_" + f'B' + "_" + f'{line + 1}' + '_' + f'{shakhes}' + "_" + f'{1}'
                                 ticket = 0
                                 execution = 0
                                 if status_trade == True:
                                     print("shakhes: True" )
                                     rec_pos = BUY_SELL.pos_buy(point_low , shakhes , lot , self.symbol_EURUSD , commands)
                                     execution = rec_pos.comment
                                     if execution == 'Request executed':
                                            ticket =  rec_pos.order
                                            print("rec_pos:" , rec_pos)
                                            print("ticket:" , ticket)
                                     
                                 command = "(Patern:" + f'{candel_num})' + " _ " + "(Type:" + f'{type})' + " _ " + "(Line:" + f'{line + 1})' + ' _ ' + "(Shakhes:" + f'{shakhes})' + " _ " + "(Pulback:" f'{1})'+ " _ " + "(Point5:" + f'{point_low})' + " _ " + "(Time:" + f'{time_command})' + " _ " + "(Sub:" + f'{tel})' + " _ " + "(Status_trade:" + f'{status_trade})' + " _ " + "(ticket:" + f'{ticket})' + " _ " + "(execution:" + f'{execution})' + " _ " + "(list_line:" + f'{cal_line})' 
                                 Database.update_table_chek(point_low , timestamp_pulback , command , "true" , ticket , candel_num)    

                         elif telo_sub_low == cal_point and cal_price_candel > tel and type == "Two_Bottom" and status_tel == True and chek == "false":
                                 print("point_low:" , point_low)
                                 print("telo_sub_low:" , telo_sub_low)  
                                 print("candel_color:" , candel_statess) 
                                 print ("line:" , line + 1)
                                 print("cal_price_candel:" , cal_price_candel)
                                 print("patern: down  22222222222222222222222222222222222222222222")
                                 print("pullback_HHHHHHHHHH")
                                 time_command = pd.to_datetime( timestamp_pulback , unit='s')
                                 shakhes = LINE.line_shakhes(candel_num , self.symbol_EURUSD , self.decimal_sambol)
                                 status_trade = shakhes[1]
                                 print("status_trade:" , status_trade)
                                 shakhes = int (shakhes[0])
                                 print("shakhes:" , shakhes)
                                 commands = f'{candel_num}' + "_" + f'B' + "_" + f'{line + 1}' + '_' + f'{shakhes}' + "_" + f'{1}'
                                 ticket = 0
                                 execution = 0
                                 if status_trade == True:
                                     print("shakhes: True" )
                                     rec_pos = BUY_SELL.pos_buy(telo_sub_low , shakhes , lot , self.symbol_EURUSD , commands)
                                     execution = rec_pos.comment
                                     if execution == 'Request executed':
                                            ticket =  rec_pos.order
                                            print("rec_pos:" , rec_pos)
                                            print("ticket:" , ticket)
                                 command = "(Patern:" + f'{candel_num})' + " _ " + "(Type:" + f'{type})' + " _ " + "(Line:" + f'{line + 1})' + ' _ ' + "(Shakhes:" + f'{shakhes})' + " _ " + "(Pulback:" f'{1})'+ " _ " + "(Point5:" + f'{telo_sub_low})' + " _ " + "(Time:" + f'{time_command})' + " _ " + "(telo_sub_low:" + f'{tel})' + " _ " + "(Status_trade:" + f'{status_trade})' + " _ " + "(ticket:" + f'{ticket})' + " _ " + "(execution:" + f'{execution})' + " _ " + "(list_line:" + f'{cal_line})' 
                                 Database.update_table_chek(telo_sub_low , timestamp_pulback , command , "true" , ticket , candel_num)    
                                  
                         elif telo_add_low == cal_point and cal_price_candel > tel and type == "Two_Bottom" and status_tel == True and chek == "false":
                                 print("point_low:" , point_low)
                                 print("telo_add_low:" , telo_add_low)
                                 print("candel_color:" , candel_statess)
                                 print ("line:" , line + 1)
                                 print("cal_price_candel:" , cal_price_candel)
                                 print("patern: down  33333333333333333333333333333333333333333333")
                                 print("pullback_HHHHHHHHHH")
                                 time_command = pd.to_datetime( timestamp_pulback , unit='s')
                                 shakhes = LINE.line_shakhes(candel_num , self.symbol_EURUSD , self.decimal_sambol)
                                 status_trade = shakhes[1]
                                 print("status_trade:" , status_trade)
                                 shakhes = int (shakhes[0])
                                 print("shakhes:" , shakhes)
                                 commands = f'{candel_num}' + "_" + f'B' + "_" + f'{line + 1}' + '_' + f'{shakhes}' + "_" + f'{1}'
                                 ticket = 0
                                 execution = 0
                                 if status_trade == True:
                                     print("shakhes: True" )
                                     rec_pos = BUY_SELL.pos_buy(telo_add_low , shakhes , lot , self.symbol_EURUSD , commands)
                                     execution = rec_pos.comment
                                     if execution == 'Request executed':
                                            ticket =  rec_pos.order
                                            print("rec_pos:" , rec_pos)
                                            print("ticket:" , ticket)
                                 command = "(Patern:" + f'{candel_num})' + " _ " + "(Type:" + f'{type})' + " _ " + "(Line:" + f'{line + 1})' + ' _ ' + "(Shakhes:" + f'{shakhes})' + " _ " + "(Pulback:" f'{1})'+ " _ " + "(Point5:" + f'{telo_add_low})' + " _ " + "(Time:" + f'{time_command})' + " _ " + "(telo_add_low:" + f'{tel})' + " _ " + "(Status_trade:" + f'{status_trade})' + " _ " + "(ticket:" + f'{ticket})' + " _ " + "(execution:" + f'{execution})' + " _ " + "(list_line:" + f'{cal_line})' 
                                 Database.update_table_chek(telo_add_low , timestamp_pulback , command , "true" , ticket , candel_num)    

 def pullback_2 (self , tel , status_tel , timestamp_pulback , lot):
       
       telo = '0.0'
       for i in range(self.decimal_sambol - 2):  
          telo = telo + "0"
          
       telo = telo + f"{tel}"  
       telo = float (telo)
     #   print("telerance:" , telo) 
      
       data_all = Database.select_table_All()
       select_all_len = len(data_all)
       if select_all_len > 0:
          # print("select_all_len:" , select_all_len)
          rec = data_all[select_all_len - 1]
          # print("rec:" , rec)


          for index in range(select_all_len):
                                     
                    # print("index:" , index)
                    lab = data_all[index]
                    candel_num = lab[1]
                    type = lab[2]
                    point_patern = lab[3]
                    timepstamp = lab[19] 
                    time_start_search = lab[17]
                    status = lab[15]
                    chek = lab[16]
             
             
                    time_start_search = int(time_start_search)
                    # print("lab:" , lab)
                    # print("status:" , status)
                    # print("time_start_search:" , time_start_search)
                    # print("point_patern:" , point_patern)
                    # print("type:" , type)
                    # print("candel_num:" , candel_num)
              
                    point_patern = json.loads(point_patern)
                    timepstamp = json.loads(timepstamp)
                    timepstamp_3 = json.loads(timepstamp[3])

                    # print("timepstamp_3:" , timepstamp_3)
                    timepstamp_old = int(timepstamp_3) + 900
                    # print("timepstamp_old:" , timepstamp_old)
                    print("Pullback 222222222222222222222222222222222222222222222222222222222222222222222222222222222")

             
                    if status == "true" and chek == "false":
                        
                        
                        list_close_plan2 = []
                        list_open_plan2 = []
                        list_timestamp_plan2 = []
                        inputs_close = mt5.copy_rates_range(self.symbol_EURUSD , mt5.TIMEFRAME_M1 , timepstamp_old , timestamp_pulback)
                        # print("inputs_close:" , inputs_close)
                        for index in inputs_close:
                            index_c = "{:.5f}".format(index[4])
                            index_o = "{:.5f}".format(index[1])
                            index_t = index[0]
                            list_close_plan2.append(index_c)
                            list_open_plan2.append(index_o)
                            list_timestamp_plan2.append(index_t)
                          #   print("index:" , index[4])
            
                    #     list_close_plan2 = ['1.09145', '1.09140', '1.09143', '1.09139', '1.09143', '1.09186', '1.09175', '1.09154', '1.09186', '1.09113', '1.09151']
                    #     list_open_plan2 = ['1.09153', '1.09145', '1.09135', '1.09145', '1.09144', '1.09143', '1.09116', '1.09159', '1.09123', '1.09124', '1.09212']
                    #     list_timestamp_plan2 = [1693473300, 1693473360, 1693473420, 1693473480, 1693473540, 1693473600, 1693473660, 1693473720, 1693473780, 1693473840, 1693473900]   
                         
                        # print("list_close_plan2:" , list_close_plan2)
                        # print("list_open_plan2:" , list_open_plan2)
                        # print("list_timestamp_plan2:" , list_timestamp_plan2)  
                        
                        for index_close , index_point_close in enumerate(list_close_plan2):   

                        #    try:            
                               
                
                               # len_inputs_close = len(inputs_close)
                               len_inputs_close = len(list_close_plan2)
                               len_inputs_open = len(list_open_plan2)
                
                               # print("list_close_plan2:" , list_close_plan2)
                               # print("list_open_plan2:" , list_open_plan2)
                
                              #  print("len_inputs_close:" , len_inputs_close)
                               
                               # print("len_inputs_open:" , len_inputs_open)
                
                               close_plan2 = 0 
                               open_plan2 = 0
                               time_stamp_plan2 = 0
                               list_point_plan2 = []
                               list_point_left_right_plan2 = []
                               list_point_group = []
                               candel_state_plan2 = ''
                               line = 0   
                               exit = 0
       
                               if len_inputs_close >= 3 and index_close >= 2:
                                   #   print("")
       
                                    #  for index_plan2 in range (2 , len_inputs_close):
                                   #   print("index_paln2:" , index_close)
                                     timestamp_plan2 = int (list_timestamp_plan2[index_close])
                                    #  print("timestamp_plan2:" , timestamp_plan2)
                                     close_plan2 = index_point_close
                                     close_plan2= float(close_plan2)
                                    #  print("close_plan2:" , close_plan2)
                                     open_plan2 = list_open_plan2[index_close]
                                     open_plan2= float(open_plan2)
                                    #  print("open_plan2:" , open_plan2)
              
                                     cal_line =  LINE.line_run(candel_num , self.symbol_EURUSD , timestamp_plan2 )
                                   #   print("cal_line:" , cal_line)
              
                                     telo_add_close_high = close_plan2 + telo
                                     telo_sub_close_low = close_plan2 - telo
                                     telo_add_close_high = "{:.5f}".format(telo_add_close_high)
                                     telo_sub_close_low = "{:.5f}".format(telo_sub_close_low)
                                     telo_sub_close_low = float(telo_sub_close_low)
                                     telo_add_close_high = float(telo_add_close_high)
                                    #  print("telo_add_close_high:" , telo_add_close_high)
                                    #  print("telo_sub_close_low:" , telo_sub_close_low)
     
                                     try:
                                         
                                           for line_point in cal_line:
              
                                                left_rigth = float(line_point)
                                             #    print("left_rigth:" , left_rigth)
                       
                                                if close_plan2 == left_rigth:
                                                       print("index_plan2:" , index_close)
                                                       list_point_plan2.append(left_rigth)
                                                       print("list_point_plan2:" , list_point_plan2)
                                                       list_point_left_right_plan2.append(float(list_close_plan2[index_close - 1]))
                                                       list_point_left_right_plan2.append(float(list_close_plan2[index_close]))
                                                       list_point_left_right_plan2.append(float(list_close_plan2[index_close + 1]))
                                                       exit = 1
                       
                                                elif telo_add_close_high ==  left_rigth:
                                                      #  print("telo_add_close_high")
                                                       list_point_plan2.append(left_rigth)
                                                      #  print("list_point_plan2:" , list_point_plan2)
                                                       list_point_left_right_plan2.append(float(list_close_plan2[index_close - 1]))
                                                       list_point_left_right_plan2.append(float(list_close_plan2[index_close]))
                                                       list_point_left_right_plan2.append(float(list_close_plan2[index_close + 1]))
                                                       exit = 1
                                                      
                                                elif telo_sub_close_low ==  left_rigth:
                                                      #  print("index_plan2:" , index_plan2)
                                                      #  print("telo_add_close_high")
                                                       list_point_plan2.append(left_rigth)
                                                      #  print("list_point_plan2:" , list_point_plan2)
                                                       list_point_left_right_plan2.append(float(list_close_plan2[index_close - 1]))
                                                       list_point_left_right_plan2.append(float(list_close_plan2[index_close]))
                                                       list_point_left_right_plan2.append(float(list_close_plan2[index_close + 1]))
                                                       exit = 1
                       
                                                if list_point_left_right_plan2 != []:
                                                    
                                                     break   
                                     except:
                                           print("list_close_plan2 eroooooooooooor")                
              
                                          #  print("list_point_left_right_plan2:" , list_point_left_right_plan2) 
                                           # print("list_point_group:" , list_point_group) 
              
                                          #  print("timestamp_plan2:" , timestamp_plan2)
                                          #  print("close_plan2:" , close_plan2)
                                          #  print("open_plan2:" , open_plan2)  
              
                                           if open_plan2 > close_plan2:
                                               candel_state_plan2 = "red"
                                  
                                           elif open_plan2 < close_plan2:
                                               candel_state_plan2 = "green"
                                              
                                           elif open_plan2 == close_plan2:
                                               candel_state_plan2 = "doji"
                    
                    
                                           left_candel_plan2 = 0
                                           right_candel_plan2 = 0
                                    
                    
                                           for index , left_rigth in enumerate(list_point_left_right_plan2):  
                                                 
                                                 if index == 0:
                                                      left_candel_plan2 = left_rigth
                             
                                                 elif index == 2:
                                                      right_candel_plan2 = left_rigth    
                    
              
                                          #  print("left_candel_plan2:" , left_candel_plan2)  
                                          #  print("right_candel_plan2:" , right_candel_plan2) 
                                          #  print("candel_state_plan2:" , candel_state_plan2)   
                                          #  print("type:" , type)  
                                           
                                           for line , gap_point in enumerate(cal_line):       
                                                 
                                                #  print("gap_point:" , gap_point)
                                                 
                                                 cal_point = gap_point  
                    
                                                 if close_plan2 == cal_point and (candel_state_plan2 == "green" or  candel_state_plan2 == "doji") and close_plan2 > left_candel_plan2 and close_plan2 > right_candel_plan2 and type == "Two_TOP":
                                                            print("UP  1111111111111111111111111111111111111111111111")
                                                            print("pullback_MMMMMMMMMM")
                                                            print ("line:" , line + 1)
                                                            time_command = pd.to_datetime( timestamp_plan2 , unit='s')
                                                            shakhes = LINE.line_shakhes(candel_num , self.symbol_EURUSD , self.decimal_sambol)
                                                            status_trade = shakhes[1]
                                                            print("status_trade:" , status_trade)
                                                            
                                                            shakhes = int (shakhes[0])
                                                            commands = f'{candel_num}' + "_" + f'B' + "_" + f'{line + 1}' + '_' + f'{shakhes}' + "_" + f'{2}'
                                                            ticket = 0
                                                            execution = 0
                                                            if status_trade == True:
                                                                 print("shakhes: True" )
                                                                 rec_pos = BUY_SELL.pos_sell(close_plan2 , shakhes , lot , self.symbol_EURUSD , commands)
                                                                 execution = rec_pos.comment
                                                                 if execution == 'Request executed':
                                                                        ticket =  rec_pos.order
                                                                        print("rec_pos:" , rec_pos)
                                                                        print("ticket:" , ticket)
                                                            command = "(Patern:" + f'{candel_num})' + " _ " + "(Type:" + f'{type})' + " _ " + "(Line:" + f'{line + 1})' + ' _ ' + "(Shakhes:" + f'{shakhes})' + " _ " + "(Pulback:" f'{2})'+ " _ " + "(Point5:" + f'{close_plan2})' + " _ " + "(Time:" + f'{time_command})' + " _ " + "(Status_trade:" + f'{status_trade})' + " _ " + "(ticket:" + f'{ticket})'+ " _ " + "(execution:" + f'{execution})' + " _ " + "(list_line:" + f'{cal_line})' 
                                                            Database.update_table_chek(close_plan2 , timestamp_pulback , command , "true" , ticket , candel_num)     

                                                            exit = 1
                                                            break
                          
                                                 elif close_plan2 == cal_point and (candel_state_plan2 == "red" or  candel_state_plan2 == "doji") and close_plan2 < left_candel_plan2 and close_plan2 < right_candel_plan2 and type == "Two_Bottom":
                                                            print("DOWN 2222222222222222222222222222222222222222222222")
                                                            print("pullback_HHHHHHHHHH")
                                                            print ("line:" , line + 1) 
                                                            time_command = pd.to_datetime( timestamp_plan2 , unit='s')
                                                            shakhes = LINE.line_shakhes(candel_num , self.symbol_EURUSD , self.decimal_sambol)
                                                            status_trade = shakhes[1]
                                                            print("status_trade:" , status_trade)
                                                            shakhes = int (shakhes[0])
                                                            commands = f'{candel_num}' + "_" + f'B' + "_" + f'{line + 1}' + '_' + f'{shakhes}' + "_" + f'{2}'
                                                            ticket = 0
                                                            execution = 0
                                                            if status_trade == True:
                                                                 print("shakhes: True" )
                                                                 rec_pos = BUY_SELL.pos_buy(close_plan2 , shakhes , lot , self.symbol_EURUSD , commands)
                                                                 execution = rec_pos.comment
                                                                 if execution == 'Request executed':
                                                                        ticket =  rec_pos.order
                                                                        print("rec_pos:" , rec_pos)
                                                                        print("ticket:" , ticket)
                                                            command = "(Patern:" + f'{candel_num})' + " _ " + "(Type:" + f'{type})' + " _ " + "(Line:" + f'{line + 1})' + ' _ ' + "(Shakhes:" + f'{shakhes})' + " _ " + "(Pulback:" f'{2})'+ " _ " + "(Point5:" + f'{close_plan2})' + " _ " + "(Time:" + f'{time_command})' + " _ " + "(Status_trade:" + f'{status_trade})' + " _ " + "(ticket:" + f'{ticket})' + " _ " + "(execution:" + f'{execution})' + " _ " + "(list_line:" + f'{cal_line})' 
                                                            Database.update_table_chek(close_plan2 , timestamp_pulback , command , "true" , ticket , candel_num)     
                                                            
                                                            exit = 1
                                                            break

                                                 elif cal_point == telo_add_close_high and (candel_state_plan2 == "green" or  candel_state_plan2 == "doji") and cal_point > left_candel_plan2 and cal_point > right_candel_plan2 and type == "Two_TOP" and  status_tel == True:
                                                            print("UP TEL 11111111111111111111111111111111111111111111")
                                                            print("pullback_MMMMMMMMMM")
                                                            print ("line:" , line + 1) 
                                                            time_command = pd.to_datetime( timestamp_plan2 , unit='s')
                                                            shakhes = LINE.line_shakhes(candel_num , self.symbol_EURUSD , self.decimal_sambol)
                                                            status_trade = shakhes[1]
                                                            print("status_trade:" , status_trade)
                                                            shakhes = int (shakhes[0])
                                                            commands = f'{candel_num}' + "_" + f'B' + "_" + f'{line + 1}' + '_' + f'{shakhes}' + "_" + f'{2}'
                                                            ticket = 0
                                                            execution = 0
                                                            if status_trade == True:
                                                                 print("shakhes: True" )
                                                                 rec_pos = BUY_SELL.pos_sell(telo_add_close_high , shakhes , lot , self.symbol_EURUSD , commands)
                                                                 execution = rec_pos.comment
                                                                 if execution == 'Request executed':
                                                                        ticket =  rec_pos.order
                                                                        print("rec_pos:" , rec_pos)
                                                                        print("ticket:" , ticket)
                                                            command = "(Patern:" + f'{candel_num})' + " _ " + "(Type:" + f'{type})' + " _ " + "(Line:" + f'{line + 1})' + ' _ ' + "(Shakhes:" + f'{shakhes})' + " _ " + "(Pulback:" f'{2})'+ " _ " + "(Point5:" + f'{telo_add_close_high})' + " _ " + "(Time:" + f'{time_command})'+ " _ " + "(telo_high:" + f'{tel})' + "_" + "(Status_trade:" + f'{status_trade})' + " _ " + "(ticket:" + f'{ticket})' + " _ " + "(execution:" + f'{execution})' + " _ " + "(list_line:" + f'{cal_line})' 
                                                            Database.update_table_chek(telo_add_close_high , timestamp_pulback , command , "true" , ticket , candel_num)     
                                                            
                                                            exit = 1
                                                            break
                          
                                                 elif cal_point == telo_sub_close_low and (candel_state_plan2 == "red" or  candel_state_plan2 == "doji") and cal_point < left_candel_plan2 and cal_point < right_candel_plan2 and type == "Two_Bottom" and  status_tel == True:
                                                            print("DOWN TEL 222222222222222222222222222222222222222222")
                                                            print("pullback_HHHHHHHHHH")
                                                            print ("line:" , line + 1)    
                                                            time_command = pd.to_datetime( timestamp_plan2 , unit='s')
                                                            shakhes = LINE.line_shakhes(candel_num , self.symbol_EURUSD , self.decimal_sambol)
                                                            status_trade = shakhes[1]
                                                            print("status_trade:" , status_trade)
                                                            shakhes = int (shakhes[0])
                                                            commands = f'{candel_num}' + "_" + f'B' + "_" + f'{line + 1}' + '_' + f'{shakhes}' + "_" + f'{2}'
                                                            ticket = 0
                                                            execution = 0
                                                            if status_trade == True:
                                                                 print("shakhes: True" )
                                                                 rec_pos = BUY_SELL.pos_buy(telo_sub_close_low , shakhes , lot , self.symbol_EURUSD , commands)
                                                                 execution = rec_pos.comment
                                                                 if execution == 'Request executed':
                                                                        ticket =  rec_pos.order
                                                                        print("rec_pos:" , rec_pos)
                                                                        print("ticket:" , ticket)

                                                            command = "(Patern:" + f'{candel_num})' + " _ " + "(Type:" + f'{type})' + " _ " + "(Line:" + f'{line + 1})' + ' _ ' + "(Shakhes:" + f'{shakhes})' + " _ " + "(Pulback:" f'{2})'+ " _ " + "(Point5:" + f'{telo_sub_close_low})' + " _ " + "(Time:" + f'{time_command})'+ " _ " + "(telo_low:" + f'{tel})' + "_" + "(Status_trade:" + f'{status_trade})' + " _ " + "(ticket:" + f'{ticket})' + " _ " + "(execution:" + f'{execution})' + " _ " + "(list_line:" + f'{cal_line})' 
                                                            Database.update_table_chek(telo_sub_close_low , timestamp_pulback , command , "true" , ticket , candel_num)     

                                                            exit = 1
                                                            break
                          
                                                 elif cal_point == telo_sub_close_low and (candel_state_plan2 == "green" or  candel_state_plan2 == "doji") and cal_point > left_candel_plan2 and cal_point > right_candel_plan2 and type == "Two_TOP" and  status_tel == True:
                                                            print("UP TEL 11111111111111111111122222222222222222222222")
                                                            print("pullback_MMMMMMMMMM")
                                                            print ("line:" , line + 1) 
                                                            time_command = pd.to_datetime( timestamp_plan2 , unit='s')
                                                            shakhes = LINE.line_shakhes(candel_num , self.symbol_EURUSD , self.decimal_sambol)
                                                            status_trade = shakhes[1]
                                                            print("status_trade:" , status_trade)
                                                            shakhes = int (shakhes[0])
                                                            commands = f'{candel_num}' + "_" + f'B' + "_" + f'{line + 1}' + '_' + f'{shakhes}' + "_" + f'{2}'
                                                            ticket = 0
                                                            execution = 0
                                                            if status_trade == True:
                                                                 print("shakhes: True" )
                                                                 rec_pos = BUY_SELL.pos_sell(telo_sub_close_low , shakhes , lot , self.symbol_EURUSD , commands)
                                                                 execution = rec_pos.comment
                                                                 if execution == 'Request executed':
                                                                        ticket =  rec_pos.order
                                                                        print("rec_pos:" , rec_pos)
                                                                        print("ticket:" , ticket)
                                                            command = "(Patern:" + f'{candel_num})' + " _ " + "(Type:" + f'{type})' + " _ " + "(Line:" + f'{line + 1})' + ' _ ' + "(Shakhes:" + f'{shakhes})' + " _ " + "(Pulback:" f'{2})'+ " _ " + "(Point5:" + f'{telo_sub_close_low})' + " _ " + "(Time:" + f'{time_command})'+ " _ " + "(Telo_high-1-2:" + f'{tel})' + "_" + "(Status_trade:" + f'{status_trade})' + " _ " + "(ticket:" + f'{ticket})' + " _ " + "(execution:" + f'{execution})' + " _ " + "(list_line:" + f'{cal_line})' 
                                                            Database.update_table_chek(telo_sub_close_low , timestamp_pulback , command , "true" , ticket , candel_num)     

                                                            exit = 1
                                                            break
                          
                                                 elif cal_point == telo_add_close_high and (candel_state_plan2 == "red" or  candel_state_plan2 == "doji") and cal_point < left_candel_plan2 and cal_point < right_candel_plan2 and type == "Two_Bottom" and  status_tel == True:
                                                            print("DOWN TEL 222222222222222222221111111111111111111111")
                                                            print("pullback_HHHHHHHHHH")
                                                            print ("line:" , line + 1)
                                                            time_command = pd.to_datetime( timestamp_plan2 , unit='s')
                                                            shakhes = LINE.line_shakhes(candel_num , self.symbol_EURUSD , self.decimal_sambol)
                                                            status_trade = shakhes[1]
                                                            print("status_trade:" , status_trade)
                                                            shakhes = int (shakhes[0])
                                                            commands = f'{candel_num}' + "_" + f'B' + "_" + f'{line + 1}' + '_' + f'{shakhes}' + "_" + f'{2}'
                                                            ticket = 0
                                                            execution = 0
                                                            if status_trade == True:
                                                                 print("shakhes: True" )
                                                                 rec_pos = BUY_SELL.pos_buy(telo_add_close_high , shakhes , lot , self.symbol_EURUSD , commands)
                                                                 execution = rec_pos.comment
                                                                 if execution == 'Request executed':
                                                                        ticket =  rec_pos.order
                                                                        print("rec_pos:" , rec_pos)
                                                                        print("ticket:" , ticket)
                                                            command = "(Patern:" + f'{candel_num})' + " _ " + "(Type:" + f'{type})' + " _ " + "(Line:" + f'{line + 1})' + ' _ ' + "(Shakhes:" + f'{shakhes})' + " _ " + "(Pulback:" f'{2})'+ " _ " + "(Point5:" + f'{telo_add_close_high})' + " _ " + "(Time:" + f'{time_command})'+ " _ " + "(Telo_high-2-1:" + f'{tel})' + "_" + "(Status_trade:" + f'{status_trade})' + " _ " + "(ticket:" + f'{ticket})' + " _ " + "(execution:" + f'{execution})' + " _ " + "(list_line:" + f'{cal_line})' 
                                                            Database.update_table_chek(telo_add_close_high , timestamp_pulback , command , "true" , ticket , candel_num)     

                                                            exit = 1
                                                            break
                                                 
                                                 else :
                                                      exit = 0
                          
                                           print("")
                                           if (exit == 1):
                                               break
                        #    except:
                        #     print("error plan2")  

 def pullback_3 (self , timestamp_pulback , list_pullback3 , lot):
               
      data_all = Database.select_table_All()
      select_all_len = len(data_all)

      if select_all_len > 0:
               
         for index in range(select_all_len):
                          
          #   print("indexs:" , index)
            lab = data_all[index]
            candel_num = lab[1]
            type = lab[2]
            point_patern = lab[3]
            status = lab[15]
            chek = lab[16]

            exit = 0
            ticket = 0
            
          #   print("select_all_len:" , select_all_len)
            rec = data_all[select_all_len - 1]
            # print("rec:" , rec)
            print("plan 333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333")

            if (status == "true" and chek == "false"):

                         
                     list_point = []
                     list_point_left_right = []
                     list_point_group = []
                     cal_line =  LINE.line_run(candel_num , self.symbol_EURUSD , timestamp_pulback )
                     print("cal_line:" , cal_line)
                    #  print("point_patern:" , point_patern)
                     
                    #  print("cal_line:" , cal_line)
                    #  print ("list_pullback3:" , list_pullback3) 
                    #  print ("timestamp_pulback:" , timestamp_pulback) 

            #    try:

                     try:
                         for indexs , index_point_close in enumerate(list_pullback3):  
                              #   print("indexs:" , indexs)  
                              #   print("index_point_close:" , index_point_close)        
                               
                                for line_point in cal_line:  
          
                                  #  print("line_point:" , line_point) 
                                 
                                   if str(line_point) ==  index_point_close:
                                   #     print("indexxx:" , indexs)
                                       list_point.append(index_point_close)
                                       list_point_left_right.append(list_pullback3[indexs - 1])
                                       list_point_left_right.append(list_pullback3[indexs])
                                       list_point_left_right.append(list_pullback3[indexs + 1])
                                   #     print("list_point_left_right:" , list_point_left_right)

                                   if list_point_left_right != []:
                                               list_point_group.append(list_point_left_right)
                                               list_point_left_right = []

                     except:
                         print("error list_pullback3[indexs + 1:")
                                     
                    #  print("list_point_group:" , list_point_group)              
                     if list_point_group != []:
          
                        # try:
                            
                             for list in list_point_group:
          
                                  list_point_left_right = list
                              #     print("list_point_left_right:" , list_point_left_right)
          
                                  for line , gap_point in enumerate(cal_line):      
                                     
                                      cal_point = gap_point
                                      cal_point = float(cal_point)
                                      left_candel = list_point_left_right[0]
                                      right_candel = list_point_left_right[2]
                                      point_close_3 = list_point_left_right[1]
                                      left_candel = float(left_candel)
                                      right_candel = float(right_candel)
                                      point_close_3 = float(point_close_3)
          
                                      rec = Database.select_table_One(candel_num)
                                      chek = rec[0][16]
                                   #    print("chek:" , chek)
                                      
                                   #    print("left_candel:" , left_candel)
                                   #    print("right_candel:" , right_candel)
                                   #    print("point_close_3:" , point_close_3)
                                   #    print("gap:" , cal_point)
          
                                      if point_close_3 == cal_point and point_close_3 > left_candel and point_close_3 > right_candel and type == "Two_TOP" and chek == "false":
                                           print("1111111111111111111111111111111111111111111111")
                                           print("point_close_3:" , point_close_3)
                                           print("left_candel:" , left_candel)
                                           print("right_candel:" , right_candel)
                                           print ("line:" , line + 1)
                                           time_command = pd.to_datetime( timestamp_pulback , unit='s')
                                           shakhes = LINE.line_shakhes(candel_num , self.symbol_EURUSD , self.decimal_sambol)
                                           status_trade = shakhes[1]
                                           print("status_trade:" , status_trade)
                                           shakhes = int (shakhes[0])
                                           commands = f'{candel_num}' + "_" + f'B' + "_" + f'{line + 1}' + '_' + f'{shakhes}' + "_" + f'{3}'
                                           ticket = 0
                                           execution = 0
                                           if status_trade == True:
                                                print("shakhes: True" )
                                                rec_pos = BUY_SELL.pos_sell(point_close_3 , shakhes , lot , self.symbol_EURUSD , commands)
                                                print("rec_pos:" , rec_pos)
                                                execution = rec_pos.comment
                                                if execution == 'Request executed':
                                                   ticket =  rec_pos.order
                                                   print("rec_pos:" , rec_pos)
                                                   print("ticket:" , ticket)
                                           command = "(Patern:" + f'{candel_num})' + " _ " + "(Type:" + f'{type})' + " _ " + "(Line:" + f'{line + 1})' + ' _ ' + "(Shakhes:" + f'{shakhes})' + " _ " + "(Pulback:" f'{3})'+ " _ " + "(Point5:" + f'{point_close_3})' + " _ " + "(Time:" + f'{time_command})' + " _ " + "(Status_trade:" + f'{status_trade})' + " _ " + "(ticket:" + f'{ticket})' + " _ " + "(execution:" + f'{execution})' + " _ " + "(list_line:" + f'{cal_line})' 
                                           Database.update_table_chek(point_close_3 , timestamp_pulback , command , "true" , ticket , candel_num)     
                                           exit = 1
                                           break
                                         
          
                                      elif point_close_3 == cal_point and point_close_3 < left_candel and point_close_3 < right_candel and type == "Two_Bottom" and chek == "false":
                                           print("22222222222222222222222222222222222222222222222")
                                           print("point_close_3:" , point_close_3)
                                           print("left_candel:" , left_candel)
                                           print("right_candel:" , right_candel)
                                           print ("line:" , line + 1)
                                           time_command = pd.to_datetime( timestamp_pulback , unit='s')
                                           shakhes = LINE.line_shakhes(candel_num , self.symbol_EURUSD , self.decimal_sambol)
                                           status_trade = shakhes[1]
                                           print("status_trade:" , status_trade)
                                           shakhes = int (shakhes[0])
                                           commands = f'{candel_num}' + "_" + f'B' + "_" + f'{line + 1}' + '_' + f'{shakhes}' + "_" + f'{3}'
                                           ticket = 0
                                           execution = 0
                                           if status_trade == True:
                                                print("shakhes: True" )
                                                rec_pos = BUY_SELL.pos_buy( point_close_3 , shakhes , lot , self.symbol_EURUSD , commands)
                                                execution = rec_pos.comment
                                                if execution == 'Request executed':
                                                   ticket =  rec_pos.order
                                                   print("rec_pos:" , rec_pos)
                                                   print("ticket:" , ticket)
                                           command = "(Patern:" + f'{candel_num})' + " _ " + "(Type:" + f'{type})' + " _ " + "(Line:" + f'{line + 1})' + ' _ ' + "(Shakhes:" + f'{shakhes})' + " _ " + "(Pulback:" f'{3})'+ " _ " + "(Point5:" + f'{point_close_3})' + " _ " + "(Time:" + f'{time_command})' + " _ " + "(Status_trade:" + f'{status_trade})'  + " _ " + "(ticket:" + f'{ticket})'+ " _ " + "(execution:" + f'{execution})' + " _ " + "(list_line:" + f'{cal_line})' 
                                           Database.update_table_chek(point_close_3 , timestamp_pulback , command , "true" , ticket , candel_num)     
                                           exit = 1
                                           break    
              

                                  if exit== 1:
                                       break
                        # except:
                        #        print("the end")     
                     

            #    except:
            #        print("error plan 33333333333") 

 def pullback_4 (self , tel , status_tel , timestamp_pulback , lot):
           
           

           telo = '0.0'
           for i in range(self.decimal_sambol - 2):  
              telo = telo + "0"
              
           telo = telo + f"{tel}"  
           telo = float (telo)
          #  print("telerance:" , telo) 
        
           data_all = Database.select_table_All()
           select_all_len = len(data_all)
           if select_all_len > 0:
          #     print("select_all_len:" , select_all_len)
              rec = data_all[select_all_len - 1]
              # print("rec:" , rec)
              
        
              for index in range(select_all_len):
               #   print("")
                                  
               #   print("index:" , index)
                 lab = data_all[index]
                 candel_num = lab[1]
                 type = lab[2]
                 point_patern = lab[3]
                 timepstamp = lab[19] 
                 time_start_search = lab[17]
                 status = lab[15]
                 chek = lab[16]
        
        
                 time_start_search = int(time_start_search)
               #   print("lab:" , lab)
               #   print("status:" , status)
               #   print("time_start_search:" , time_start_search)
               #   print("point_patern:" , point_patern)
               #   print("type:" , type)
               #   print("candel_num:" , candel_num)
           
                 point_patern = json.loads(point_patern)
                 timepstamp = json.loads(timepstamp)
                 timepstamp_3 = json.loads(timepstamp[3])

               #   print("timepstamp_3:" , timepstamp_3)

                 timepstamp_old = int(timepstamp_3) + 900
               #   print("timepstamp_old:" , timepstamp_old)
               
                 print("Pullback 4444444444444444444444444444444444444444444444444444444444444444444444444444")


                 if status == "true" and chek == "false":

                     inputs_candels = mt5.copy_rates_range(self.symbol_EURUSD, mt5.TIMEFRAME_M1, timepstamp_old, timestamp_pulback)
                    #  print("inputs_candels:" , inputs_candels)

                     for candel_recive in inputs_candels:
                         # print("candel_recive:" , candel_recive)  


                         timestamp_pulback4 = candel_recive[0]
                         timestamp_pulback4 = int(timestamp_pulback4)
                         # print("timestamp_pulback4:" , timestamp_pulback4)  

                         timestamp_pulback_p = timestamp_pulback4 - 60
                         timestamp_pullback_n = timestamp_pulback4 + 60
                         # print("timestamp_pulback_p:" , timestamp_pulback_p)
                         # print( pd.to_datetime( timestamp_pulback_p , unit='s'))
                         # print("timestamp_pullback_n:" , timestamp_pullback_n)
                         # print( pd.to_datetime( timestamp_pullback_n , unit='s'))  
                         
                         
                         point_open = "{:.5f}".format(candel_recive[1])
                         point_open = float(point_open)
                         # print ("point_open:" , point_open)

                         point_close = "{:.5f}".format(candel_recive[4])
                         point_close = float(point_close)
                         # print ("point_close:" , point_close)
          
                         point_close_p = mt5.copy_rates_from(self.symbol_EURUSD , mt5.TIMEFRAME_M1 , timestamp_pulback_p  , 1)
                         point_close_p = "{:.5f}".format(point_close_p[0][4])
                         point_close_p = float(point_close_p)
                         # print ("point_close_p:" , point_close_p)

                         point_open_n = mt5.copy_rates_from(self.symbol_EURUSD , mt5.TIMEFRAME_M1 , timestamp_pullback_n , 1)
                         point_open_n = "{:.5f}".format(point_open_n[0][1])
                         point_open_n = float(point_open_n)
                         # print ("point_open:" , point_open_n)
                 
                 
                         candel_state = ''
                         if point_open > point_close:
                           candel_state = "red"
                         elif point_open < point_close:
                           candel_state = "green"
                         elif point_open == point_close:
                           candel_state = "doji"  
                 
                         # print("candel_state:" , candel_state)
                 
                         # cal_point = LINE.cal_point_line(1 , timestamp_pulback)
                         # print("cal_point:" , cal_point)
                         cal_line =  LINE.line_run(candel_num , self.symbol_EURUSD , timestamp_pulback )
                         # print("cal_line:" , cal_line)


                         if (candel_state == "red" and point_open > point_close_p and type == "Two_TOP"):

                              for line , gap_point in enumerate(cal_line):
                                    cal_point = float(gap_point)
                                   #  print("cal_point:" , cal_point)

                                    if point_open == cal_point:
                                           print("1111111111111111111111111111111111111111111111")
                                           print("point_open:" , point_open)
                                           print ("line:" , line + 1)
                                           print("pullback MMMMMMMMMMMMMMMM")
                                           time_command = pd.to_datetime( timestamp_pulback , unit='s')
                                           shakhes = LINE.line_shakhes(candel_num , self.symbol_EURUSD , self.decimal_sambol)
                                           status_trade = shakhes[1]
                                           print("status_trade:" , status_trade)
                                           
                                           shakhes = int (shakhes[0])
                                           commands = f'{candel_num}' + "_" + f'B' + "_" + f'{line + 1}' + '_' + f'{shakhes}' + "_" + f'{4}'
                                           ticket = 0
                                           execution = 0
                                           if status_trade == True:
                                                print("shakhes: True" )
                                                rec_pos = BUY_SELL.pos_sell(point_open , shakhes , lot , self.symbol_EURUSD , commands)
                                                execution = rec_pos.comment
                                                if execution == 'Request executed':
                                                   ticket =  rec_pos.order
                                                   print("rec_pos:" , rec_pos)
                                                   print("ticket:" , ticket)
                                           command = "(Patern:" + f'{candel_num})' + " _ " + "(Type:" + f'{type})' + " _ " + "(Line:" + f'{line + 1})' + ' _ ' + "(Shakhes:" + f'{shakhes})' + " _ " + "(Pulback:" f'{4})'+ " _ " + "(Point5:" + f'{point_open})' + " _ " + "(Time:" + f'{time_command})' + " _ " + "(candel_state: red)" + " _ " + "(Status_trade:" + f'{status_trade})' + " _ " + "(ticket:" + f'{ticket})'+ " _ " + "(execution:" + f'{execution})' + " _ " + "(list_line:" + f'{cal_line})' 
                                           Database.update_table_chek(point_open , timestamp_pulback , command , "true" , ticket , candel_num)      

                         elif (candel_state == "green" and point_open < point_close_p and type == "Two_Bottom"):

                              for line , gap_point in enumerate(cal_line):
                                    cal_point = float(gap_point)
                                   #  print("cal_point:" , cal_point)

                                    if point_open == cal_point:
                                           print("2222222222222222222222222222222222222222222222")
                                           print("point_open:" , point_open)
                                           print ("line:" , line + 1)
                                           print("pullback HHHHHHHHHHHHHHHH")
                                           time_command = pd.to_datetime( timestamp_pulback , unit='s')
                                           shakhes = LINE.line_shakhes(candel_num , self.symbol_EURUSD , self.decimal_sambol)
                                           status_trade = shakhes[1]
                                           print("status_trade:" , status_trade)
                                           shakhes = int (shakhes[0])
                                           commands = f'{candel_num}' + "_" + f'B' + "_" + f'{line + 1}' + '_' + f'{shakhes}' + "_" + f'{4}'
                                           ticket = 0
                                           execution = 0
                                           if status_trade == True:
                                                print("shakhes: True" )
                                                rec_pos = BUY_SELL.pos_buy(point_open , shakhes , lot , self.symbol_EURUSD , commands)
                                                execution = rec_pos.comment
                                                if execution == 'Request executed':
                                                   ticket =  rec_pos.order
                                                   print("rec_pos:" , rec_pos)
                                                   print("ticket:" , ticket)
                                           command = "(Patern:" + f'{candel_num})' + " _ " + "(Type:" + f'{type})' + " _ " + "(Line:" + f'{line + 1})' + ' _ ' + "(Shakhes:" + f'{shakhes})' + " _ " + "(Pulback:" f'{4})'+ " _ " + "(Point5:" + f'{point_open})' + " _ " + "(Time:" + f'{time_command})' + " _ " + "(candel_state: green)" + "(Status_trade:" + f'{status_trade})' + " _ " + "(ticket:" + f'{ticket})'+ " _ " + "(execution:" + f'{execution})' + " _ " + "(list_line:" + f'{cal_line})' 
                                           Database.update_table_chek(point_open , timestamp_pulback , command , "true" , ticket , candel_num)     
                                                          
                         if (candel_state == 'doji' and point_open > point_close_p and point_open > point_open_n and type == "Two_TOP"):

                              for line , gap_point in enumerate(cal_line):
                                    cal_point = float(gap_point)
                                   #  print("cal_point:" , cal_point)

                                    if point_open == cal_point:
                                           print("1111111111111111111111111111111111111111111111")
                                           print("point_open:" , point_open)
                                           print ("line:" , line + 1)
                                           print("pullback MMMMMMMMMMMMMMMM") 
                                           time_command = pd.to_datetime( timestamp_pulback , unit='s')
                                           shakhes = LINE.line_shakhes(candel_num , self.symbol_EURUSD , self.decimal_sambol)
                                           status_trade = shakhes[1]
                                           print("status_trade:" , status_trade)
                                           shakhes = int (shakhes[0])
                                           commands = f'{candel_num}' + "_" + f'B' + "_" + f'{line + 1}' + '_' + f'{shakhes}' + "_" + f'{4}'
                                           ticket = 0
                                           execution = 0
                                           if status_trade == True:
                                                print("shakhes: True" )
                                                rec_pos = BUY_SELL.pos_sell(point_open , shakhes , lot , self.symbol_EURUSD , commands)
                                                execution = rec_pos.comment
                                                if execution == 'Request executed':
                                                   ticket =  rec_pos.order
                                                   print("rec_pos:" , rec_pos)
                                                   print("ticket:" , ticket)
                                           command = "(Patern:" + f'{candel_num})' + " _ " + "(Type:" + f'{type})' + " _ " + "(Line:" + f'{line + 1})' + ' _ ' + "(Shakhes:" + f'{shakhes})' + " _ " + "(Pulback:" f'{4})'+ " _ " + "(Point5:" + f'{point_open})' + " _ " + "(Time:" + f'{time_command})' + " _ " + "(candel_state: doji)"  + " _ " + "(Status_trade:" + f'{status_trade})' + " _ " + "(ticket:" + f'{ticket})'+ " _ " + "(execution:" + f'{execution})' + " _ " + "(list_line:" + f'{cal_line})' 
                                           Database.update_table_chek(point_open , timestamp_pulback , command , "true" , ticket , candel_num)        
                                          
                         elif (candel_state == "doji" and point_open < point_close_p and point_open < point_open_n and type == "Two_Bottom"):

                              for line , gap_point in enumerate(cal_line):
                                    cal_point = float(gap_point)
                                   #  print("cal_point:" , cal_point)

                                    if point_open == cal_point:
                                           print("22222222222222222222222222222222222222222")
                                           print("point_open:" , point_open)
                                           print ("line:" , line + 1)
                                           print("pullback HHHHHHHHHHHHHHHHHH")
                                           time_command = pd.to_datetime( timestamp_pulback , unit='s')
                                           shakhes = LINE.line_shakhes(candel_num , self.symbol_EURUSD , self.decimal_sambol)
                                           status_trade = shakhes[1]
                                           print("status_trade:" , status_trade)
                                           shakhes = int (shakhes[0])
                                           commands = f'{candel_num}' + "_" + f'B' + "_" + f'{line + 1}' + '_' + f'{shakhes}' + "_" + f'{4}'
                                           ticket = 0
                                           execution = 0
                                           if status_trade == True:
                                                print("shakhes: True" )
                                                rec_pos = BUY_SELL.pos_buy( point_open , shakhes , lot , self.symbol_EURUSD , commands)
                                                execution = rec_pos.comment
                                                if execution == 'Request executed':
                                                   ticket =  rec_pos.order
                                                   print("rec_pos:" , rec_pos)
                                                   print("ticket:" , ticket)
                                           command = "(Patern:" + f'{candel_num})' + " _ " + "(Type:" + f'{type})' + " _ " + "(Line:" + f'{line + 1})' + ' _ ' + "(Shakhes:" + f'{shakhes})' + " _ " + "(Pulback:" f'{4})'+ " _ " + "(Point5:" + f'{point_open})' + " _ " + "(Time:" + f'{time_command})' + " _ " + "(candel_state: doji)"  + " _ " + "(Status_trade:" + f'{status_trade})' + " _ " + "(ticket:" + f'{ticket})'+ " _ " + "(execution:" + f'{execution})' + " _ " + "(list_line:" + f'{cal_line})' 
                                           Database.update_table_chek(point_open , timestamp_pulback , command , "true" , ticket , candel_num)


