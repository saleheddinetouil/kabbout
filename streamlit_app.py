import streamlit as st
import pandas as pd
from game import TunisianRamiGame, Player
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

    # Replace the section to display the current scores as a CTF scoreboard
    st.header("Current Scores 🏆")
    current_scores_df = pd.DataFrame({
    'Player': list(game.get_current_scores().keys()),
    'Score': list(game.get_current_scores().values())
})
    current_scores_df = current_scores_df.sort_values(by='Score', ascending=False).reset_index(drop=True)
    st.table(current_scores_df)

# Replace the section to display the round based scores as line charts
    st.header("Round Based Scores")
    if game.round_history:
        round_scores_df = pd.DataFrame(game.round_history)
        st.line_chart(round_scores_df)
    else:
        st.write("No rounds recorded yet.")
    
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
    threading.Thread(target=auto_save, daemon=True).start()
    main()