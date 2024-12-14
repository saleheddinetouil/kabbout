import streamlit as st
import pandas as pd
from game import TunisianRamiGame, Player

st.set_page_config(page_title="Tunisian Rami Scorekeeper", page_icon="🃏", layout="wide")

def initialize_game(player_names):
    if 'game' not in st.session_state:
        st.session_state.game = TunisianRamiGame(player_names)

def main():
    st.title("Tunisian Rami Scorekeeper 🃏🇹🇳")

    st.sidebar.header("Game Setup")
    num_players = st.sidebar.number_input("Number of Players:", min_value=2, max_value=4, value=4)
    default_player_names = ["Saleh", "Player 2", "Player 3", "Player 4"]
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
        game.save_game()

    st.header("Current Scores 🏆")
    st.bar_chart(pd.DataFrame([game.get_current_scores()]).transpose())

    st.header("Round History 📚")
    if game.round_history:
        st.table(game.get_round_history_dataframe())
    else:
        st.write("No rounds recorded yet.")

    st.header("Round Based Scores")
    if game.round_history:
        for i, round_scores in enumerate(game.round_history):
            st.subheader(f"Round {i+1}")
            st.bar_chart(pd.DataFrame([round_scores]).transpose())
    else:
        st.write("No rounds recorded yet.")

if __name__ == "__main__":
    main()
