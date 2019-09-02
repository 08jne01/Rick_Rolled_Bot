#Rick-Rolled Bot
import praw
from praw.models import MoreComments
from praw.models import Comment
import lxml
import urllib
import re
import numpy as np
import time
from lxml import etree
import os
import thread
import sys

#sys.stdout=open("console.log", "a+")

class Bot:

	def __init__(self, bot_name, sub):
		#Reddit
		self.reddit = praw.Reddit(bot_name)
		self.subreddit = self.reddit.subreddit(sub)
		self.time_start = time.time()
		self.comment_queue = []
		self.pm_queue = []
		self.comment_queue_main = []
		self.get_regex()
		self.make_files()
		self.get_ids()
		self.open_id()
		self.link_regex = re.compile(
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')

	def get_regex(self):
		input_titles = open("titles_for_regex.txt", 'r')
		title_regex_lines = input_titles.read().split('\n')
		input_titles.close()
		title_regex = []

		for i in title_regex_lines:
			line = i.split(',')
			new_line = []
			for j in line:
				new_line.append(j.rstrip('\r'))
			title_regex.append(new_line)

		self.regexs = []

		for i in title_regex:
			buffer = []
			for j in i:
				buffer.append(re.compile(j, re.IGNORECASE | re.DOTALL))
			self.regexs.append(buffer)

	def make_files(self):
		#First time run function
		exists = os.path.isfile('read_ids.txt')
		if (exists):
			print "Skipping first time setup: read_ids.txt"
		else:
			try:
				read_file = open("read_ids.txt", 'a+')
				read_file.close()
			except Exception, e:
				print ("Function: make_files, read_ids")
				print ("EXCEPTION: " + str(e))
		
		exists = os.path.isfile('RickRolls.txt')
		if (exists):
			print "Skipping first time setup: RickRolls.txt"
		else:
			try:
				read_file = open("RickRolls.txt", 'a+')
				read_file.close()
			except Exception, e:
				print ("Function: make_files, RickRolls")
				print ("EXCEPTION: " + str(e))
	
	def get_ids(self):
		#Get Ids at start
		try:
			input_ids_file = open("read_ids.txt", 'r')
			ids_local = input_ids_file.read().split('\n')
			input_ids_file.close()
			self.read_ids = []
			for i in ids_local:
				self.read_ids.append(i.rstrip('\r'))
			
			if (len(self.read_ids) > 100):
				self.read_ids = self.read_ids[-100:]

		except Exception, e:
			print ("Function: get_ids")
			print ("EXCEPTION: " + str(e))

	def append_ids(self, comment):
		#Write read ids to file and append to variable list of read ids
		try:
			self.id_write_file.write(str(comment.id) + '\n')
			if (len(self.read_ids) > 100):
				self.read_ids.pop(0)
			self.read_ids.append(str(comment.id))
		except Exception, e:
			print ("Function: append_ids")
			print ("EXCEPTION: " + str(e))

	def write_ids(self):
		for i in self.read_ids:
				self.id_write_file.write(str(i) + '\n')

	def check_id(self, comment):
		#Check read_ids vs comment id
		try:
			regex_id = re.compile('(' + str(comment.id) + ')', )
			if (regex_id.search(str(self.read_ids))):
				print ("Skipping: " + str(comment.id))
				return 0
			else:
				return 1
		except Exception, e:
			print ("Function: check_id")
			print ("EXCEPTION: " + str(e))

	def open_id(self):
		try:
			self.id_write_file = open("read_ids.txt", 'a+')
		except Exception, e:
			print ("Function: open_id")
			print ("EXCEPTION: " + str(e))

	def close_id(self):
		try:
			for i in self.read_ids:
				self.id_write_file.write(str(i) + '\n')
			self.id_write_file.close()
		except Exception, e:
			print ("Function: close_id")
			print ("EXCEPTION: " + str(e))

	def get_link(self, comment):
		try:
			link = self.link_regex.search(comment.body.encode('ascii', 'ignore'))
			if (link):
				return link.group()
			else:
				return 0
		except Exception, e:
			print ("Function: get_link")
			print ("EXCEPTION: " + str(e))

	def get_title(self, link):
		try:
			youtube = etree.HTML(urllib.urlopen(link).read())
			video_title = str(youtube.xpath("//span[@id='eow-title']/@title"))
			return video_title
		except Exception, e:
			print ("Function: get_title")
			print ("EXCEPTION: " + str(e))

	
	def match_title(self, regexs_local, title):
		n = 0
		for i in regexs_local:
			if (i.search(title)):
				n+=1
		if (n > len(regexs_local)-1):
			return 1
		else:
			return 0

	def check_title(self, title):
		for i in self.regexs:
			if (self.match_title(i, title)):
				return 1
		return 0

	def console_log(self, comment, link):
		try:
			rick_roll_file = open("RickRolls.txt", 'a+')
			print("==================")
			print ("Found Rick-Roll: " + str(comment.id))
			print ("Body: " + comment.body.encode('ascii', 'ignore'))
			print link
			print("==================")
			string = "==================\nFound Rick-Roll: " + str(comment.id) + "\nBody: " + comment.body.encode('ascii', 'ignore') + "\n" + link + '\n'
			rick_roll_file.write(string)
			rick_roll_file.close()
		except Exception, e:
			print ("Function: console_log")
			print ("EXCEPTION: " + str(e))

	def send_replies_as_pm(self):
		message_subject = "rick_rolled_bot found some!"
		message_body = ""
		spacer = "===================" + "  \n\n"
		try:
			for i in self.pm_queue:
				message_body += spacer + i.body.encode('ascii', 'ignore') + "  \n\n" + "URL: " + i.permalink + "  \n\n"
			self.pm_queue = []

			self.reddit.redditor('JNelson_').message(message_subject, message_body)
		except Exception, e:
			print ("Function: send_replies_as_pm")
			print ("EXCEPTION: " + str(e))


	def add_reply_to_pm_q(self, comment):
		self.pm_queue.append(comment)
		if (len(self.pm_queue) > 19):
			self.send_replies_as_pm()

	def reply_to_commment(self, comment):
		try:
			if (comment.author.name != "AutoModerator"):
				output_replies = open("replies.txt", 'a+')
				my_comment = comment.reply("#The above comment likely contains a rick roll!\n\n^(Beep boop: downvote to delete)")
				output_replies.write(str(my_comment.id) + '\n')
				output_replies.close()
				self.add_reply_to_pm_q(comment)
		except Exception, e:
			print ("Function: reply_to_comment")
			print ("EXCEPTION: " + str(e))

	def get_my_replies(self):
		try:
			replies = []
			me = self.reddit.redditor('rick_rolled_bot')
			for comment in me.comments.new(limit=None):
				replies.append(comment)
			if (len(replies) > 0):
				return replies
			else:
				return 0
		except Exception, e:
			print ("Function: get_my_replies")
			print ("EXCEPTION: " + str(e))

	def check_delete(self, time_check):
		if (time.time() - self.time_start > time_check):
			#print replies
			replies = self.get_my_replies()

			if (replies):
				replies.reverse()
				print("==================")
				print("Checking comment scores")
				for my_comment in replies:
					try:
						n = my_comment.score
						i = my_comment.id
						author = my_comment.author
						#Check for author and score
						if (n < -2 and author != None):
							print("Deleting comment " + str(i) + " Score: " + str(n))
							my_comment.delete()
						elif (author == None):
							print("[Deleted]")
							#print("Deleted Comment " + str(i) + " Score: " + str(n))
						#else:
							#print("Comment " + str(i) + " Score: " + str(n))
					except Exception, e:
						print ("Function: check_delete, second")
						print ("EXCEPTION: " + str(i) + '\n' + str(e)) 
				print("==================")
			self.time_start = time.time()

			try:
				self.close_id()
				erase = open("read_ids.txt", 'w')
				for i in self.read_ids:
					erase.write(i + '\n')
				erase.close()
				self.open_id()
			except Exception, e:
				print ("Function: check_delete, third")
				print ("EXCEPTION: " + str(e))

	def check_queue(self, thread_name):
		try:
			while (True):
				while (len(self.comment_queue) > 0):
					comment_from_q = self.comment_queue.pop(0)
					if (self.check_id(comment_from_q)):
						self.append_ids(comment_from_q)
						#print len(self.comment_queue)
						link = self.get_link(comment_from_q)
						if (link):
							title = self.get_title(link)
							if (title != None):
								if (self.check_title(title)):
									#Found one
									self.console_log(comment_from_q, link)
									self.reply_to_commment(comment_from_q)
				self.check_delete(240) #default 240

				#print("1")
		except (KeyboardInterrupt, SystemExit), e:
			print ("========Closing Down========")
			self.close_id()
		except Exception, e:
			print ("Function: check_queue")
			print ("EXCEPTION: " + str(e))
			

	def main_loop(self):
		try:
			while (True):
				try:
					for comment in self.subreddit.stream.comments(pause_after=-1):
						#sys.stdout.flush()
						if (comment != None):
							#print len(self.comment_queue_main)
							self.comment_queue.append(comment)
								#Append id to read_ids
								#print len(self.read_ids)		
				except (KeyboardInterrupt, SystemExit), e:
					print ("========Closing Down========")
					self.close_id()
				except Exception, e:
					print ("Function: main_loop")
					print ("EXCEPTION: " + str(e))
		except (KeyboardInterrupt, SystemExit), e:
			print ("========Closing Down========")
			self.close_id()
		
		

def main():
	
	bot = Bot('rick_rolled_bot', 'all')

	#print bot.check_title('Rick Astley - Never Gonna Give You Up (Video)')
	thread.start_new_thread(bot.check_queue, ("Thread",))

	#bot.check_delete(-1)
	bot.main_loop()

if __name__ == '__main__':
	main()
	#sys.stdout.close()
