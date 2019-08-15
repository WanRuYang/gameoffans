import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table

import plotly.plotly as py
import plotly.graph_objs as go

import sd_material_ui

from server import server
from model import run_model
import json
import pandas as pd
import emoji
import re

import logging
import traceback

import psycopg2

pg_conn = psycopg2.connect(database='reddit',
                           user='', 
                           password='', 
                           host='localhost', 
                           port='5432')

app = dash.Dash(
    __name__,
    server=server,
    assets_folder='static',
    assets_url_path='static',
    external_stylesheets=['static/styles.css'],
)

#select * from movies where lower(title) like lower('%Lion%');
cur = pg_conn.cursor()  
q = """SELECT DISTINCT m.title, p.m1
       FROM posts p
       INNER JOIN movies m ON p.m1 = m.id
       WHERE m.id IN ('tt0107290','tt1475582','tt1431045','tt0068646','tt0133093',
                 'tt0120685','tt0114709','tt2737304','tt1727824','tt0892769')
       """
cur.execute(q)
res = cur.fetchall()
res

variable_name = dict(res)
app.title = 'game of fans'
app.layout = html.Div(
    # style={'vertical-align': 'middle'},
    className='some-paper-wrapper',
    children=[
    html.Div(html.H1('GAME OF FANS', className='H1'), 
        className='banner'),
    dcc.Markdown(children="""
        # Please pick a film to get what's threading on /r/frick!! 
     """, className="left",
    ), 
  
    html.A(html.Img(src=app.get_asset_url('icons8-linkedin.svg'),
                    style={"float": "right", "position": "relative",
                   "width": "5%", "height": "auto", "margin-right": "20px",
                   "display":"inline-block"}),
        href='https://www.linkedin.com/in/WanRuYang', target="_blank"),
    html.A(html.Img(src=app.get_asset_url('icons8-github.svg'),
                    style={"float": "right", "position": "relative",
                   "width": "5%", "height": "auto", 
                   "display":"inline-block"}),
        href='https://github.com/WanRuYang/gameoffans', target="_blank"),

    html.Div(children=[
      html.Div(
        id='input-warpper', 
        children=[
          dcc.Dropdown(
            id='movies-list',
            options=[{'label': k, 'value': v} for k, v in variable_name.items()],
            placeholder= 'Select a film:',
            multi=False,
            className='review-textarea',
            style={'width':'78%', 'margin-left':'80px'}
            ),
          dcc.Markdown('# Or ..... search by keyword(s)!',
            className="left",
            style={"margin-top": "20px"}),
          # dcc.Markdown(children="""Or ..... search by Keyord(s)! 
             # """, className="left",), 
          dcc.Textarea(
            id='review-textarea',
            placeholder='recommend',
            className = 'review-textarea',
            # value= 'recommend',
          ),
          sd_material_ui.FlatButton(
            id='submit-query', label='Submit', 
            backgroundColor='#2196f3', 
            n_clicks=0
          ),
          html.Img(id='review-sentiment-icon', className='purple-column')
        ],
        className='purple-column'
      ),
      html.Div(id='movie-info', className='blue-column'),
      html.Img(id='movie-cover', className='green-column',
                style={'height':'50vh', 'width':'auto'}),    
      ], className='row' ),
      html.Div(id='reddit_posts'),
    ])

@app.callback(
    [   Output('movie-info', 'children'),
        Output('reddit_posts', 'children'),
        # Output('reddit_comments', 'children'),
        Output('review-sentiment-icon', 'src'),
        Output('movie-cover', 'src'),
    ],
    [Input('submit-query', 'n_clicks')],
    [State('movies-list', 'value'),
    State('review-textarea', 'value')],
)

def submit_review(n_clicks, item, user_text):
    if user_text is not None and str(item).startswith('tt'):
      return (
      'Pick one from the menu OR keyword search',
      '........',
      'static/r2.png',
      'static/neg2.png'
      )

    movie_info = ''
    src_cover = f'static/noinput.png'
    # print ('...............time', item)
    if item is None:
      print ('...............time', item)
    else:
      movie_info = query_movie_info(item)
      src_cover = f'static/{item}.jpg'

    movie_info_out = ''
    names = ['Title','Rating', 'Released', 'Language', 'Country', 'Director','Awards', 'Actors']
    if movie_info != '':
      for key, val in enumerate(movie_info.split(';')):
        movie_info_out = movie_info_out + "## 🧿 {} : {} \n".format(names[key], val) 
        posts = query_title(item)
        sent = query_sentiment(item)
    else:
      # print(f'!!!!!!!!!!!!!!{user_text}')
      posts = query_title(user_text)
      sent = query_sentiment(user_text)

    if sent is None:
      src = ''
    elif sent < -0.1:
      src = f"static/neg3.gif"
    elif sent > 0.1:
      src = f"static/happy.png"
    else:
      src = f"static/neg1.png"
      
    if type(posts) == str :
      # print('no posts')
      return (
          dcc.Markdown(movie_info_out),
          html.P(posts),
          '',
          src_cover
      )
    ids = posts.id.tolist()
    comments =query_comment(ids)

    if type(comments) == str:
      # print('no comments')
      return (
          dcc.Markdown(movie_info_out),
          html.P(comments),
          'static/neg2',
          src_cover
      )

    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~', posts.head())
    post = posts.title + posts.text
    comm = comments.text

    res = ''
    for key, val in enumerate(post):
      res = res + "# 🧿 {} \n".format(val)
      for k2, val2 in enumerate(comm): #<span style="font-family:Papyrus; font-size:4em;">LOVE!</span>
          res+= "## {} : {}\n".format(k2+1, val2) 
    print(res)
    if n_clicks > 0:
      print('n_clicks')
      return (    
          dcc.Markdown(movie_info_out),         
          dcc.Markdown(res),#children = res),
          src,
          src_cover
      )
    else:
      return (
          html.H1(''),
          html.H1(''),
          '',
          ''
      )

# @app.callback(
#     [ Output('submit-query', 'children'),
#       Output('review-textarea', 'children'),
#     ],
#     [Input('submit-query', 'n_clicks')],
#     [State('movies-list', 'value'),
#     State('review-textarea', 'value')],
# )
# def update(n_clicks, list_itme, text):
#     return 0, 'Recommend'

def query_movie_info(input, pg_conn=pg_conn):
    # print('got input........................', input)
    res = ''
    cur = pg_conn.cursor()
    try:
        q = f"""
            SELECT id, title, rating, released, language, country, director, awards, actors 
            FROM movies
            WHERE id = '{input}' LIMIT 1;"""
        cur.execute(q)
    except psycopg2.DatabaseError as e:
        app.logger.error(f'Unable to query user table for login status, reason: {e}, type: {type(e)}, traceback: {traceback.format_exc()}')
        pg_conn.rollback()

    res = cur.fetchall()
    res = ';'.join([str(x) for x in res[0][1:]])
    print(f'current string :{res}')
    return res

def query_title(input_str, pg_conn = pg_conn):
    cur = pg_conn.cursor()
    res = ''
    if input_str is not None and re.match('tt\d+', input_str):
      try:# TODO toggle spiler
            q = f"""
                SELECT id, score, title, selftext FROM posts p
                WHERE p.m1 = '{input_str}'  AND p.pred = False 
                ORDER BY p.score DESC, p.num_comments DESC LIMIT 20
                ;"""
            # print(q)
            cur.execute(q)
      except psycopg2.DatabaseError as e:
        app.logger.error(f'Unable to query user table for login status, reason: {e}, type: {type(e)}, traceback: {traceback.format_exc()}')
        pg_conn.rollback()
        # res = cur.fetchall()
        # res = pd.DataFrame(res, columns = ['id', 'score', 'text', 'pred'])
        # # if all(res.pred == True):
        # return res

    else:
      try:
          q = f"""
              SELECT id, score, title, selftext FROM posts p
              WHERE lower(p.title) LIKE lower('%{input_str}%') AND 
                    p.pred = FALSE 
              ORDER BY p.score DESC , p.num_comments DESC LIMIT 20
              ;"""
          print(q)
          cur.execute(q)
      except psycopg2.DatabaseError as e:
        app.logger.error(f'Unable to query user table for login status, reason: {e}, type: {type(e)}, traceback: {traceback.format_exc()}')
        pg_conn.rollback()

    res = cur.fetchall()
    res = pd.DataFrame(res, columns = ['id', 'score', 'title' ,'text'])
    # print(res)
    if len(res) == 0:
      return ('No thread found 🍔')
    # res = pd.DataFrame(res, columns = ['id', 'score', 'text'])
    res.title = res.title.apply(emoji.emojize)
    res.text = res.text.apply(emoji.emojize)
    return res

def query_comment(input, pg_conn = pg_conn):

    cur = pg_conn.cursor()
    try:  #('{"','".join(input)}')    
    ## TO DO update query to top 5 of each group 
        cur.execute(f"""
        SELECT link_id, score, body FROM 
             (SELECT link_id, score, body, 
              RANK() OVER (PARTITION BY link_id ORDER BY score DESC) AS rk 
              FROM comments WHERE link_id IN ('{"','".join(input)}')) t 
        WHERE RK <=3 
            ;""")
    except psycopg2.DatabaseError as e:
        app.logger.error(f'Unable to query comments table, reason: {e}, type: {type(e)}, traceback: {traceback.format_exc()}')
        pg_conn.rollback()

    res = cur.fetchall()
    if len(res) == 0:
      return ('No thread found 😲')    
    res = pd.DataFrame(res, columns = ['id', 'score','text'])
    res.text = res.text.apply(emoji.emojize)
    return res


def query_sentiment(input_str = 'star wars'):
  import re
  cur = pg_conn.cursor()
  print('query...........................', input_str)
  if input_str is not None and re.match('tt\d+', input_str):
      # NO way to verfiy the film tile by string match 
    try:   # currently average over all result have to group by 
      q = f""" 
          WITH tb AS (SELECT id, vader 
              FROM posts 
              WHERE m1 = '{input_str}' or\
                    m2 = '{input_str}' or \
                    m3 = '{input_str}'
              ), 
               tb2 AS (
                  SELECT vader FROM comments 
                  WHERE link_id IN (SELECT DISTINCT id FROM tb)
                  UNION 
                  SELECT vader FROM tb)
           SELECT avg(vader) FROM tb2
          ;"""
      cur.execute(q)

    except psycopg2.DatabaseError as e:
      app.logger.error(f'Uable to query posts table, reason: {e}, type: {type(e)}, traceback: {traceback.format_exc()}')
      pg_conn.rollback()
    # res = cur.fetchall()

  else:
    try:   # currently average over all result have to group by 
      cur.execute(f""" 
          WITH tb AS (SELECT id, vader 
              FROM posts 
              WHERE lower(title) LIKE lower('%{input_str}%')
              ), 
               tb2 AS (
                  SELECT vader FROM comments 
                  WHERE link_id IN (SELECT DISTINCT id FROM tb)
                  UNION 
                  SELECT vader FROM tb)
           SELECT avg(vader) FROM tb2
          ;""")

    except psycopg2.DatabaseError as e:
      app.logger.error(f'Uable to query posts table, reason: {e}, type: {type(e)}, traceback: {traceback.format_exc()}')
      pg_conn.rollback()
  res = cur.fetchall()
  # print(res)
  return res[0][0] 


if __name__ == '__main__':

    import sys

    logging.basicConfig(
        format='%(asctime)-15s %(levelname)-8s %(message)s',
        level=logging.INFO,
        stream=sys.stdout,
    )

    app.run_server(port=80, host='0.0.0.0', debug=True)
