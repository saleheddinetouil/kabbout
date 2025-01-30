import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from game import TunisianRamiGame, Player  # Assuming your game logic is in 'game.py'
import threading
import time

st.set_page_config(page_title="Tunisian Rami Scorekeeper", page_icon="🃏", layout="wide")

def initialize_game(player_names):
    if 'game' not in st.session_state:
        st.session_state.game = TunisianRamiGame(player_names)
        st.session_state.game.load_from_json()

def auto_save():
    while True:
        if 'game' in st.session_state:
            game = st.session_state.game
            game.save_to_json()
        time.sleep(60)

def create_ctf_scoreboard(game):
    """
    Creates a CTF-style scoreboard that shows the current ranking and cumulative scores
    after each round, similar to how a CTF scoreboard evolves over time.
    """
    if not game.round_history:
        st.write("No rounds recorded yet.")
        return

    # Create a DataFrame to hold the cumulative scores after each round
    scoreboard_data = []
    cumulative_scores = {player: 0 for player in game.players} 

    for round_num, round_scores in enumerate(game.round_history):
        for player, score in round_scores.items():
            cumulative_scores[player] += score
        
        # Sort players by cumulative score after each round
        sorted_scores = sorted(cumulative_scores.items(), key=lambda x: x[1], reverse=True)
        scoreboard_data.append(sorted_scores)

    # Prepare data for the Plotly table
    rounds = list(range(1, len(game.round_history) + 1))
    players = list(game.players.keys())
    header_values = ['Round'] + players
    cell_values = [rounds]

    for player in players:
        player_scores = []
        for round_data in scoreboard_data:
            score = next((score for p, score in round_data if p == player), 0)
            player_scores.append(score)
        cell_values.append(player_scores)
    
    
    # Create the Plotly table
    fig = go.Figure(data=[go.Table(
        header=dict(values=header_values,
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=cell_values,
                   fill_color='lavender',
                   align='left'))
    ])

    fig.update_layout(title="CTF-Style Scoreboard (Cumulative Scores by Round)")
    st.plotly_chart(fig)

def main():
    st.title("Tunisian Rami Scorekeeper 🃏🇹🇳")

    st.sidebar.header("Game Setup")
    num_players = st.sidebar.number_input("Number of Players:", min_value=2, max_value=4, value=4)
    default_player_names = ["Saleh", "Khalil", "Achref", "Morta"]
    player_names = [st.sidebar.text_input(f"Player {i+1} Name:", value=name) for i, name in enumerate(default_player_names[:num_players])]

    initialize_game(player_names)
    game = st.session_state.game

    if st.sidebar.button("New Game"):
        game.reset_game()
        game.players = {name: Player(name) for name in player_names}
        st.session_state.game = game
        st.success("New game started!")

    st.header("Score Adjustments 🎲")
    cols = st.columns(len(game.players))
    round_scores = {}

    for i, (player_name, player) in enumerate(game.players.items()):
        with cols[i]:
            round_scores[player_name] = st.number_input(f"Adjust {player_name}'s score:", value=0, step=50)

    if st.button("Record Round ➡️"):
        game.record_round(round_scores)
        st.success("Round recorded!")

    # CTF-style scoreboard
    st.header("CTF-Style Scoreboard 🏆")
    create_ctf_scoreboard(game)

    # Round Based Scores as Line Charts (Similar to your original code)
    st.header("Round Based Scores (Line Chart)")
    if game.round_history:
        rounds = list(range(1, len(game.round_history) + 1))
        round_scores_df = pd.DataFrame(game.round_history)
        round_scores_df['Round'] = rounds
        round_scores_df = round_scores_df.melt(id_vars=['Round'], var_name='Player', value_name='Score')
        st.line_chart(round_scores_df.pivot(index='Round', columns='Player', values='Score'))
    else:
        st.write("No rounds recorded yet.")

    st.header("Round History 📚")
    if game.round_history:
        st.table(game.get_round_history_dataframe())
    else:
        st.write("No rounds recorded yet.")

if __name__ == "__main__":
    threading.Thread(target=auto_save, daemon=True).start()
    main()