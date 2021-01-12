from datetime import datetime
import json

file = open('Hangouts.json','r',encoding='ascii',errors='ignore') #File to be parsed must be named Hangouts.json and must be in same directory as script

f = 0 #Counter variable for which conversation is being parsed
data = json.load(file)
iterator = len(data['conversations'])

while f < iterator:
   filename = 'output_' + str(f) + '.csv' #Output filename
   fileout = open(filename,'a', encoding="ascii")
   fileout.write('Sender ID|Sender Name|Time (UTC)|Event_Type|Message\n')
   
   conversations=data['conversations']
   conversation_dict = conversations[f] #Selects the f'th conversation
   chat = conversation_dict['conversation']
   participant_data = chat['conversation']['participant_data']
   plen = len(participant_data)
   participant_list = [None] * plen #Initializes a list to hold the participants
   j = 0
   while j < plen:
      participant_list[j] = participant_data[j]
      j = j+1

   chat_events = conversation_dict['events']
   length = len(chat_events) #The length of this is equal to the number of messages in the chat
   i = 0
   while i < length:
      chat_event = chat_events[i]
      sender_chat_id = chat_event['sender_id']['chat_id']
      
      #Find the person name from the participant list
      k = 0
      name = 'No Name'
      while k < plen:
         name_dict = participant_list[k]
         if name_dict['id']['chat_id'] == sender_chat_id:
           name = name_dict['fallback_name']
         k = k+1
         
      time_str = chat_event['timestamp']
      time_int = int(time_str)/1000000 
      time = datetime.utcfromtimestamp(time_int).strftime('%Y-%m-%d %H:%M:%S') # Converts message time to human readable
      
      event_type = chat_event['event_type']
      if event_type == 'REGULAR_CHAT_MESSAGE':
         
         if 'segment' in chat_event['chat_message']['message_content']:
            seg_len = len(chat_event['chat_message']['message_content']['segment']) #Chat messages can have multiple segments, so this is a loop to pull each segment
            counter = 0
            msg = ''
            while counter < seg_len:
              
               if chat_event['chat_message']['message_content']['segment'][counter]['type'] == 'TEXT' or chat_event['chat_message']['message_content']['segment'][counter]['type'] == 'LINK':
                  msg_seg = chat_event['chat_message']['message_content']['segment'][counter]['text'] 
                  msg = msg + ' ' + msg_seg
                  counter = counter + 1
               elif chat_event['chat_message']['message_content']['segment'][counter]['type'] == 'LINE_BREAK':
                  msg_seg = '\\n  ' #This is to represent that there was a line break
                  msg = msg + ' ' + msg_seg
                  counter = counter+1
               else:
                  print('Unidentified type in chat %s message %s' % (str(f), str(i))) #This is if a type I have not seen yet is in the message. This can be modified if other chat types are identified.
                  break
             
         elif 'attachment' in chat_event['chat_message']['message_content']:
            
            att_len = len(chat_event['chat_message']['message_content']['attachment']) #There can be multiple attachments, so this loop accounts for those
            att_counter = 0
            while att_counter < att_len:
               attachment_dict = chat_event['chat_message']['message_content']['attachment'][att_counter] 
               if attachment_dict['embed_item']['type'][att_counter] == 'PLUS_PHOTO':
                  msg = attachment_dict['embed_item']['plus_photo']['url']
               else:
                  msg = 'SOME ATTACHMENT NOT A PLUS PHOTO' #If other attachment types are identified this can be changed. All I have seen are PLUS_PHOTO types
               att_counter = att_counter + 1
               
         else:
            msg = 'Unidentified Content'
      elif event_type == 'HANGOUT_EVENT':
          msg = chat_event['hangout_event']['event_type'] #This is for Hangout calls
       
      else:
          msg = ('Unidentified content\n') #This is for unknown event types
      i = i+1
      fileout.write('%s|%s|%s|%s|%s\n' % (sender_chat_id, name, time, event_type, msg))
   fileout.close()
   f = f+1
file.close()