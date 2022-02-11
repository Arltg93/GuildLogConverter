# TODO: 
# Colorcoding für Gilden (https://stackoverflow.com/questions/287871/how-to-print-colored-text-to-the-terminal)
#                        (https://stackabuse.com/how-to-print-colored-text-in-python/)


import os
import sys
import re
import time
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#import numpy as np

def get_colors_for_guilds(guilds):
  colors = {}
  for index, guild in enumerate(guilds):
    #colors[guild] = '\\' + '033' + '[3' + f'{index+1}m'
    colors[guild] = f'\033[1;3{index+1}m'
  return colors

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
    self.score = kills*2
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


def show_killdistribution(df, colors):
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


def show_kills_per_life(df, playername, colors):
  lifes = 20
  kpl_df = df[(df.KilledPlayer == playername) | (df.KillingPlayer == playername)]
  guild_color = colors[df[df.KillingPlayer == playername].KillingGuild.unique()[0]]
  kills_in_current_life = ''
  string_length_killer = max([len(x) for x in df.KillingPlayer.unique()])
  print(f'{guild_color} Life | {"Killer".ljust(string_length_killer)} | Kills')
  print( '-----------------------------------------------')
  for index in kpl_df.index.unique():
    if kpl_df.at[index, 'KilledPlayer'] == playername:
      killer = kpl_df.at[index, 'KillingPlayer']
      killer_guild_color = colors[df[df.KillingPlayer == killer].KillingGuild.unique()[0]]
      print(f'{guild_color}  {" " if lifes < 10 else ""}{lifes}  | {killer_guild_color}{killer.ljust(string_length_killer)} {guild_color}| {kills_in_current_life} ')
      kills_in_current_life = ''
      lifes -= 1
    else:
      killer = kpl_df.at[index, 'KilledPlayer']
      kills_in_current_life += f'{colors[df[df.KillingPlayer == killer].KillingGuild.unique()[0]]}{killer}  '
  print(color.RESET)


def print_player_summary(df, playername, colors):
  kills = df[df.KillingPlayer == playername].shape[0]
  deaths = df[df.KilledPlayer == playername].shape[0]
  players_df = df.groupby(['KillingPlayer']).sum()
  guild_color = colors[df[df.KillingPlayer == playername].KillingGuild.unique()[0]] 
  ranking = sorted(players_df.kills.unique(), reverse = True)
  rank = [index for (index, item) in enumerate(ranking) if item == players_df.at[playername, 'kills']][0] + 1
  print('\n# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # \n')
  print(f'{guild_color} Spieler:  {color.UNDERLINE}{playername}{color.RESET}{guild_color}') 
  print(f' Score: {kills*2}  |  Kills: {kills}  |  Deaths: {deaths}  |  K/D: {np.round(kills/deaths,2)}  |  Rank: {rank} {"(MVP)" if rank == 1 else ""}\n')
  print(color.RESET)


def print_guild_summary(df, guildname, colors):
  guild_color = colors[guildname]
  guild_kills_df = df[df.KillingGuild == guildname]
  guild_deaths_df = df[df.KilledGuild == guildname]
  players_df = guild_kills_df.groupby(['KillingPlayer']).sum()
  print('\n# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # \n')
  print(f'{guild_color} Gilde:  {color.UNDERLINE}{guildname}{color.RESET}')
  print(f'{guild_color} Punkte: {guild_kills_df.kills.sum()*2}  |  Kills: {guild_kills_df.kills.sum()}  |  Deaths = {guild_deaths_df.kills.sum()}')
  print('')
  players_string = f'{guild_color} Spieler: '
  for player in guild_kills_df.KillingPlayer.unique():
    players_string += f'{player} ({players_df.at[player, "kills"]*2}),  '
  print(players_string)

  print(f'\n {color.RESET}Kills:')
  kills_str = ''
  for killer in guild_kills_df.KilledPlayer.to_list():
    kills_str += f'{colors[df[df.KillingPlayer == killer].KillingGuild.unique()[0]]}{killer}  '
  print(kills_str)

  ### TODO:
  # Check if this ...
  print(f'\n {color.RESET} Deaths:')
  deaths_str = ''
  for kill in guild_deaths_df.KillingPlayer.to_list():
    deaths_str += f'{colors[df[df.KillingPlayer == kill].KillingGuild.unique()[0]]}{kill}  '
  print(deaths_str)
  # ... can be outsourced into function
  print(color.RESET)


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
  df = convert_guildlog_to_df(args.log)

  # identify player for which stats shall be displayed
  playernames = [args.playername] if args.playername != '' else calc_ranking(df)

  # show guildsummary
  guilds = []
  for playername in playernames:
    guilds.append(df[df.KillingPlayer == playername].KillingGuild.unique()[0])
  colors = get_colors_for_guilds(df.KillingGuild.unique())
  for guild in guilds:
    print_guild_summary(df, guild, colors)
  
  # show player stats
  for playername in playernames:
    print_player_summary(df, playername, colors)
    show_kills_per_life(df, playername, colors)
    
  # show kill distribution in a pie chart
  show_killdistribution(df, colors)


if __name__ == "__main__":
  main()