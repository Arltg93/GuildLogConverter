# TODO: Colorcoding für Gilden (https://stackoverflow.com/questions/287871/how-to-print-colored-text-to-the-terminal)


import os
import sys
import re
import time
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def get_colors_for_guilds(guilds):
  colors = {}
  pass

class color():
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'


class Player():
  def __init__(self, name, guild, kills, deaths, kd):
    self.name = name
    self.guild = guild
    self.kills = kills
    self.deaths = deaths
    self.kd = kills/deaths


class Guild():
  def __init__(self, name, players, kills, deaths, score):
    self.name = name
    self.players = players
    self.kills = kills
    self.deaths = deaths
    self.score = kills*2
    

def convert_guildlog_to_df(guildwar_log, save_as_csv: bool = False):
  relevant_values = ['KillingGuild', 'KillingPlayer', 'KilledGuild', 'KilledPlayer']
  regex_string = r'\[(?P<KillingGuild>[\w]*)\] .*?((?P<KillingPlayer>[\w]*)\(Stufe 2\)) Angriffskraft .*?\[(?P<KilledGuild>[\w]*)\].*?(?P<KilledPlayer>[\w]*)\n'

  df = pd.DataFrame([], columns = relevant_values)
  
  with open(guildwar_log, 'r') as f:
    content = [line for line in f.readlines() if line.startswith('[')]

  for line in content:
    regex_result = re.search(regex_string, line)

    df = df.append({'KillingGuild' : regex_result.group('KillingGuild'), 
                    'KillingPlayer' : regex_result.group('KillingPlayer'), 
                    'KilledGuild' : regex_result.group('KilledGuild'), 
                    'KilledPlayer' : regex_result.group('KilledPlayer')}
                    , ignore_index = True)

  if save_as_csv:
    df.to_csv(os.path.join(os.path.dirname(guildwar_log), f'GuildWar_{time.strftime("%Y%m%d", time.localtime())}.csv'))

  df['kills'] = 1

  return df


def show_killdistribution(df):
  fig, plot = plt.subplots(ncols=2)
  
  killingguild_df = df.groupby(['KillingGuild']).sum()
  killingguild_df.sort_values(by=['kills'], inplace=True)
  killingguild_df.plot.pie( ax = plot[0], 
                            y = 'kills', 
                            figsize=(20,20), 
                            autopct='%1.1f%%', 
                            explode = [0.02 for _ in range(killingguild_df.shape[0])], 
                            legend = False, 
                            ylabel = '', 
                            title = 'Kills pro Gilde')

  killingplayer_df = df.groupby(['KillingPlayer']).sum()
  killingplayer_df.sort_values(by=['kills'], inplace=True)
  killingplayer_df.plot.pie(ax = plot[1], 
                            y = 'kills', 
                            figsize=(20,20), 
                            autopct='%1.1f%%', 
                            explode = [0.05 for _ in range(killingplayer_df.shape[0])], 
                            legend = False, 
                            ylabel = '',
                            title = 'Kills pro Spieler')

  #plt.show()


def show_kills_per_life(df, playername = None):
  lifes = 20
  kpl_df = df[(df.KilledPlayer == playername) | (df.KillingPlayer == playername)]
  kills_in_current_life = []
  string_length_killer = max([len(x) for x in df.KillingPlayer.unique()])
  print(f' Life | {"Killer".ljust(string_length_killer)} | Kills')
  print( '-----------------------------------------------')
  for index in kpl_df.index.unique():
    if kpl_df.at[index, 'KilledPlayer'] == playername:
      killer = kpl_df.at[index, 'KillingPlayer']
      print(f'  {" " if lifes < 10 else ""}{lifes}  | {killer.ljust(string_length_killer)} | {kills_in_current_life if len(kills_in_current_life) > 0 else ""} ')
      kills_in_current_life.clear()
      lifes -= 1
    else:
      kills_in_current_life.append(kpl_df.at[index, 'KilledPlayer'])


def print_player_summary(df, playername):
  kills = df[df.KillingPlayer == playername].shape[0]
  deaths = df[df.KilledPlayer == playername].shape[0]
  players_df = df.groupby(['KillingPlayer']).sum()
  ranking = sorted(players_df.kills.unique(), reverse = True)
  rank = [index for (index, item) in enumerate(ranking) if item == players_df.at[playername, 'kills']][0] + 1
  print('\n# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # \n')
  print(f' Spieler:  {playername}') 
  print(f' Score: {kills*2}  |  Kills: {kills}  |  Deaths: {deaths}  |  K/D: {kills/deaths}  |  Rank: {rank} {"(MVP)" if rank == 1 else ""}\n')


def print_guild_summary(df, guildname):
  guild_kills_df = df[df.KillingGuild == guildname]
  guild_deaths_df = df[df.KilledGuild == guildname]
  players_df = guild_kills_df.groupby(['KillingPlayer']).sum()
  print('\n# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # \n')
  print(f' Gilde:  {guildname}  |  Punkte: {guild_kills_df.kills.sum()*2}  |  Kills: {guild_kills_df.kills.sum()}  |  Deaths = {guild_deaths_df.kills.sum()}')
  print('')
  players_string = ' Spieler: '
  for player in guild_kills_df.KillingPlayer.unique():
    players_string += f'{player} ({players_df.at[player, "kills"]*2}),  '
  print(players_string)
  print(f'\n Kills:')
  print(guild_kills_df.KilledPlayer.to_list())
  print(f'\n Deaths:')
  print(guild_kills_df.KillingPlayer.to_list())



def calc_ranking(df):
  players_df = df.groupby(['KillingPlayer']).sum()
  players_df = players_df.sort_values(by='kills', ascending=False)
  return players_df.index.unique()


def collect_args():
  parser = argparse.ArgumentParser(description='Process some integers.')
  parser.add_argument('-log'          , dest='log'        , type=str, help='path to guildwar_log.txt file'    , default = os.path.join(os.path.dirname(__file__), 'test', 'GuildLog_20220209.txt'))
  parser.add_argument('-p', '--player', dest='playername' , type=str, help='playername that shall be observed', default='')

  return parser.parse_args()


def main():
  
  args = collect_args()

  # convert guildlog into pandas.DataFrame
  df = convert_guildlog_to_df(args['log'])

  # identify player for which stats shall be displayed
  playernames = [args['playername']] if args['playername'] != '' else calc_ranking(df)

  # show guildsummary
  guilds = []
  for playername in playernames:
    guilds.append(df[df.KillingPlayer == playername].KillingGuild.unique()[0])
  for guild in guilds:
    print_guild_summary(df, guild)
  
  # show player stats
  for playername in playernames:
    print_player_summary(df, playername)
    show_kills_per_life(df, playername)
    
  # show kill distribution in a pie chart
  show_killdistribution(df)


if __name__ == "__main__":
  main()