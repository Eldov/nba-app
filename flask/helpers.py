import pandas as pd
from datetime import datetime

def convertDate(a):
    try:
        date_obj = datetime.strptime(a, '%Y-%m-%d')
        return date_obj.strftime('%m/%d/%Y')
    except ValueError:
        return "Only 'YYYY-MM-DD' format is allowed"

def testId(a):
    try:      
  	   int(a)
    except:
        raise TypeError("Only integers are allowed")
    return int(a)

def groupGame(games):
    games.loc[games['MATCHUP'].str.contains('@'), 'AWAY_TEAM'] = games['MATCHUP'].str.split(' @ ', expand=True)[0]
    games.loc[games['MATCHUP'].str.contains('@'), 'HOME_TEAM'] = games['MATCHUP'].str.split(' @ ', expand=True)[1]
    games.loc[games['MATCHUP'].str.contains('vs'), 'HOME_SCORE'] = games['PTS']
    atgames = games[games['MATCHUP'].str.contains('@')]
    atgames = atgames.rename(columns={'PTS': 'AWAY_SCORE'})
    vsgames = games[games['MATCHUP'].str.contains('vs')]
    merged_df = pd.merge(atgames, vsgames[['GAME_ID', 'HOME_SCORE']], on='GAME_ID')
    merged_df = merged_df.rename(columns={'HOME_SCORE_y': 'HOME_SCORE'})
    cleandf = merged_df.loc[:, ['GAME_ID', 'GAME_DATE', 'MATCHUP', 'HOME_TEAM', 'AWAY_TEAM', 'HOME_SCORE', 'AWAY_SCORE']]
    cleandf['WINNER'] = cleandf.loc[cleandf['HOME_SCORE'] > cleandf['AWAY_SCORE'], 'HOME_TEAM']
    cleandf['WINNER'] = cleandf['WINNER'].fillna(cleandf['AWAY_TEAM'])
    return cleandf

def cleanId(data):
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date']).dt.strftime("%Y-%m-%d")
    df = df.drop(["period", "postseason", "season", "status", "time"], axis=1).rename(
        columns={
            "id": "GAME_ID",
            "date": "GAME_DATE",
            "home_team": "HOME_TEAM",
            "home_team_score": "HOME_SCORE",
            "visitor_team": "AWAY_TEAM",
            "visitor_team_score": "AWAY_SCORE",
        }
    )
    selected_row = df.loc[df.index == "full_name"].reset_index(drop=True).to_dict(orient='records')
    return selected_row

def teamsStats(df):
    avg_pts = df.groupby('TEAM_NAME')['PTS'].mean()
    avg_pts_home = df[df['MATCHUP'].str.contains('vs')].groupby('TEAM_NAME')['PTS'].mean().fillna(0).astype(int)
    avg_pts_away = df[df['MATCHUP'].str.contains('@')].groupby('TEAM_NAME')['PTS'].mean()
    total_games = df.groupby('TEAM_NAME')['WL'].count()
    total_wins = df[df['WL'] == 'W'].groupby('TEAM_NAME')['WL'].count()
    total_loss = df[df['WL'] == 'L'].groupby('TEAM_NAME')['WL'].count()
    win_percentage = (total_wins / total_games) * 100
    los_percentage = (total_loss / total_games) * 100
    new_df = pd.DataFrame({'PTS_AVG': avg_pts,
                           'HOME_AVG': avg_pts_home,
                           'AWAY_AVG': avg_pts_away,
                           'TOTAL_GAMES': total_games,
                           'TOTAL_WIN': total_wins,
                           'TOTAL_LOSS': total_loss,
                           'WIN_PERCENTAGE': win_percentage,
                           'LOSS_PERCENTAGE': los_percentage,}).reset_index()

    new_df['PTS_AVG'] = new_df['PTS_AVG'].fillna(0).astype(int)
    new_df['HOME_AVG'] = new_df['HOME_AVG'].fillna(0).astype(int)
    new_df['AWAY_AVG'] = new_df['AWAY_AVG'].fillna(0).astype(int)
    new_df['TOTAL_GAMES'] = new_df['TOTAL_GAMES'].fillna(0).astype(int)
    new_df['TOTAL_WIN'] = new_df['TOTAL_WIN'].fillna(0).astype(int)
    new_df['TOTAL_LOSS'] = new_df['TOTAL_LOSS'].fillna(0).astype(int)
    new_df['WIN_PERCENTAGE'] = new_df['WIN_PERCENTAGE'].fillna(0).astype(int)
    new_df['LOSS_PERCENTAGE'] = new_df['LOSS_PERCENTAGE'].fillna(0).astype(int)
    return new_df
