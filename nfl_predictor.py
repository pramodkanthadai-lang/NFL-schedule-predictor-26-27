"""
NFL 2026 Schedule Predictor - Professional Application
=====================================================
A polished, full-featured application for predicting the 2026 NFL season.

Features:
- Interactive team schedule management
- Real-time record updates across all 32 teams
- Collapsible team sections for clean navigation
- Visual game outcome indicators (Win/Loss/Tie)
- Complete prediction reset functionality

Author: Created with Professional Standards
Version: 1.0.0
"""

import tkinter as tk
from tkinter import ttk, messagebox
from nfl_schedule_data import NFL_SCHEDULE, normalize_team_name


# ========================
# Color Palette Constants
# ========================
class ColorPalette:
    """Professional color scheme for the application"""
    # Primary Colors (Dark Mode)
    DARK_HEADER = "#0d0d0d"
    DARK_ACCENT = "#1e1e1e"
    LIGHT_BG = "#1a1a1a"
    WHITE = "#2a2a2a"
    
    # Game Result Colors (Dark Mode - Adjusted Backgrounds)
    WIN_LIGHT = "#1b3d1b"
    WIN_DARK = "#4caf50"
    WIN_TEXT = "#81c784"
    
    LOSS_LIGHT = "#3d1b1b"
    LOSS_DARK = "#f44336"
    LOSS_TEXT = "#ef5350"
    
    TIE_LIGHT = "#3d3d1b"
    TIE_DARK = "#fbc02d"
    TIE_TEXT = "#fdd835"
    
    # UI Elements (Dark Mode)
    BORDER = "#404040"
    TEXT_PRIMARY = "#e0e0e0"
    TEXT_SECONDARY = "#a0a0a0"
    BUTTON_HOVER = "#2a2a2a"
    DANGER = "#e74c3c"


class NFLPredictor:
    def __init__(self, root):
        """
        Initialize the NFL Predictor application.
        
        Args:
            root (tk.Tk): The root tkinter window
        """
        self.root = root
        self.root.title("NFL 2026 Schedule Predictor")
        self.root.geometry("1200x800")
        self.root.configure(bg=ColorPalette.LIGHT_BG)
        self.root.minsize(1000, 600)  # Set minimum window size
        
        # =====================
        # Data Storage Variables
        # =====================
        # Game results storage: {(team1, team2, zone): result}
        # zone: "home" or "away", result: "home_win", "away_win", or "tie"
        self.game_results = {}
        
        # Team records dictionary: {team_name: {"wins": int, "losses": int, "ties": int}}
        self.team_records = {}
        self.initialize_records()
        
        # =====================
        # State Management Variables
        # =====================
        # Track which teams are currently expanded
        self.expanded_teams = set()
        
        # UI Component References
        self.game_boxes = {}         # Store references to game box widgets
        self.team_labels = {}        # Store references to team header buttons
        self.team_frames = {}        # Store references to team containers
        self.games_frames = {}       # Store references to games display frames
        
        # Build the user interface
        self.create_ui()
    
    def initialize_records(self):
        """
        Initialize team records to 0-0-0 (0 wins, 0 losses, 0 ties).
        This method resets all team records to their starting state.
        """
        for team in NFL_SCHEDULE.keys():
            self.team_records[team] = {"wins": 0, "losses": 0, "ties": 0}
    
    def create_ui(self):
        """
        Build the complete user interface for the application.
        This includes the header, instructions, scrollable team list, and footer.
        """
        # ==================
        # Header Section
        # ==================
        title_frame = tk.Frame(self.root, bg=ColorPalette.DARK_HEADER, height=70)
        title_frame.pack(fill=tk.X)
        
        # Application Title
        title_label = tk.Label(
            title_frame,
            text="🏈 NFL 2026 Schedule Predictor",
            font=("Segoe UI", 26, "bold"),
            bg=ColorPalette.DARK_HEADER,
            fg="#ffffff",
            pady=12
        )
        title_label.pack()
        
        # Subtitle/Instructions
        instructions = tk.Label(
            self.root,
            text="Click a team to expand and predict their games. Green = Win | Red = Loss | Yellow = Tie",
            font=("Segoe UI", 10),
            bg=ColorPalette.LIGHT_BG,
            fg=ColorPalette.TEXT_SECONDARY,
            pady=8
        )
        instructions.pack()
        
        # ==================
        # Main Content Section
        # ==================
        main_frame = tk.Frame(self.root, bg=ColorPalette.LIGHT_BG)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        
        # Create scrollable area for team list
        canvas = tk.Canvas(
            main_frame,
            bg=ColorPalette.LIGHT_BG,
            highlightthickness=0,
            relief=tk.FLAT
        )
        
        # Scrollbar for canvas
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=ColorPalette.LIGHT_BG)
        
        # Configure scrollbar behavior
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Populate scrollable frame with all teams
        # Teams are sorted alphabetically for consistent navigation
        for team_name in sorted(NFL_SCHEDULE.keys()):
            self.create_collapsible_team(scrollable_frame, team_name)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # ==================
        # Footer Section
        # ==================
        footer_frame = tk.Frame(self.root, bg=ColorPalette.DARK_ACCENT, relief=tk.RAISED, bd=1)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Reset Button - for clearing all predictions
        reset_button = tk.Button(
            footer_frame,
            text="↻ Reset All Predictions",
            command=self.reset_all,
            bg=ColorPalette.DANGER,
            fg="#ffffff",
            font=("Segoe UI", 11, "bold"),
            padx=20,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2",
            activebackground="#c0392b",
            activeforeground="#ffffff"
        )
        reset_button.pack(pady=10)
    
    def create_collapsible_team(self, parent, team_name):
        """
        Create a collapsible team section with expandable game schedule.
        
        Args:
            parent (tk.Frame): Parent frame to contain the team section
            team_name (str): Name of the NFL team
        """
        # Create main container for the team section
        team_container = tk.Frame(
            parent,
            bg=ColorPalette.WHITE,
            relief=tk.FLAT,
            bd=0,
            highlightthickness=1,
            highlightbackground=ColorPalette.BORDER
        )
        team_container.pack(fill=tk.X, pady=6, padx=4)
        
        # Store reference for future updates
        self.team_frames[team_name] = team_container
        
        # ==================
        # Team Header Button
        # ==================
        # Build the record string (format: W-L or W-L-T if there are ties)
        record = self.team_records[team_name]
        record_str = (
            f"{record['wins']}-{record['losses']}-{record['ties']}"
            if record['ties'] > 0
            else f"{record['wins']}-{record['losses']}"
        )
        
        # Create clickable header that toggles team expansion
        header_button = tk.Button(
            team_container,
            text=f"▶ {team_name} ({record_str})",
            font=("Segoe UI", 12, "bold"),
            bg=ColorPalette.DARK_ACCENT,
            fg="#e0e0e0",
            anchor="w",
            padx=15,
            pady=14,
            relief=tk.FLAT,
            cursor="hand2",
            command=lambda: self.toggle_team(team_name),
            activebackground=ColorPalette.BUTTON_HOVER,
            activeforeground="#81c784"
        )
        header_button.pack(fill=tk.X)
        
        # Store reference to header button for updating records
        self.team_labels[team_name] = header_button
        
        # ==================
        # Games Display Frame
        # ==================
        # This frame contains all games for the team (initially hidden)
        games_frame = tk.Frame(team_container, bg=ColorPalette.WHITE)
        games_frame.pack(fill=tk.X, padx=15, pady=10)
        games_frame.pack_forget()  # Hide until team is expanded
        
        # Get team schedule from data
        team_data = NFL_SCHEDULE[team_name]
        home_opponents = team_data["home"]
        away_opponents = team_data["away"]
        
        # Combine home and away games into single list
        # Each element is (opponent_name, is_home_game)
        all_opponents = [(opp, True) for opp in home_opponents] + \
                       [(opp, False) for opp in away_opponents]
        
        # Display games in rows of 3 for optimal layout
        for i in range(0, len(all_opponents), 3):
            row_frame = tk.Frame(games_frame, bg=ColorPalette.WHITE)
            row_frame.pack(fill=tk.X, pady=8)
            
            # Create up to 3 game boxes per row
            for j in range(3):
                if i + j < len(all_opponents):
                    opponent, is_home = all_opponents[i + j]
                    opponent = normalize_team_name(opponent)
                    self.create_game_box(row_frame, team_name, opponent, is_home)
        
        # Store reference to games frame for toggling visibility
        if not hasattr(self, 'games_frames'):
            self.games_frames = {}
        self.games_frames[team_name] = games_frame
    
    def toggle_team(self, team_name):
        """
        Toggle the expansion/collapse state of a team's schedule.
        Updates the visual arrow indicator (▶/▼) to reflect the current state.
        
        Args:
            team_name (str): Name of the team to toggle
        """
        games_frame = self.games_frames[team_name]
        header_button = self.team_labels[team_name]
        
        # Check if team is currently expanded
        if team_name in self.expanded_teams:
            # COLLAPSE: Hide games and reset arrow
            self.expanded_teams.remove(team_name)
            games_frame.pack_forget()
            
            # Update header button text with collapsed arrow
            record = self.team_records[team_name]
            record_str = (
                f"{record['wins']}-{record['losses']}-{record['ties']}"
                if record['ties'] > 0
                else f"{record['wins']}-{record['losses']}"
            )
            header_button.config(text=f"▶ {team_name} ({record_str})")
        else:
            # EXPAND: Show games and update arrow
            self.expanded_teams.add(team_name)
            games_frame.pack(fill=tk.X, padx=15, pady=10)
            
            # Update header button text with expanded arrow
            record = self.team_records[team_name]
            record_str = (
                f"{record['wins']}-{record['losses']}-{record['ties']}"
                if record['ties'] > 0
                else f"{record['wins']}-{record['losses']}"
            )
            header_button.config(text=f"▼ {team_name} ({record_str})")
    
    def create_game_box(self, parent, team, opponent, is_home):
        """
        Create an individual game box with Win/Loss/Tie prediction buttons.
        
        Each game box displays:
        - Opponent name with "vs" (home) or "@" (away) indicator
        - Three buttons for prediction: Win (W), Loss (L), Tie (T)
        - Color-coded visual feedback based on selected outcome
        
        Args:
            parent (tk.Frame): Parent frame to contain the game box
            team (str): The team playing the game
            opponent (str): The opponent team name
            is_home (bool): True if this is a home game, False for away
        """
        # Create game box frame with subtle styling
        game_frame = tk.Frame(
            parent,
            bg=ColorPalette.WHITE,
            relief=tk.FLAT,
            bd=0
        )
        game_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # ==================
        # Game Label (Opponent)
        # ==================
        # Display "vs" for home games, "@" for away games
        vs_text = "vs" if is_home else "@"
        game_label = tk.Label(
            game_frame,
            text=f"{vs_text} {opponent}",
            font=("Segoe UI", 10, "bold"),
            bg=ColorPalette.WHITE,
            fg=ColorPalette.TEXT_PRIMARY,
            anchor="w",
            padx=8,
            pady=8
        )
        game_label.pack(fill=tk.X)
        
        # ==================
        # Prediction Buttons
        # ==================
        buttons_frame = tk.Frame(game_frame, bg=ColorPalette.WHITE)
        buttons_frame.pack(fill=tk.X, padx=8, pady=(0, 8))
        
        # Create unique identifier for this game
        game_key = self.create_game_key(team, opponent, is_home)
        
        # WIN BUTTON (Green)
        win_btn = tk.Button(
            buttons_frame,
            text="W",
            width=4,
            font=("Segoe UI", 9, "bold"),
            bg=ColorPalette.WIN_LIGHT,
            fg=ColorPalette.WIN_TEXT,
            activebackground=ColorPalette.WIN_DARK,
            activeforeground=ColorPalette.WHITE,
            relief=tk.FLAT,
            cursor="hand2",
            command=lambda: self.set_game_result(
                team, opponent, is_home,
                "home_win" if is_home else "away_win"
            )
        )
        win_btn.pack(side=tk.LEFT, padx=2)
        
        # LOSS BUTTON (Red)
        loss_btn = tk.Button(
            buttons_frame,
            text="L",
            width=4,
            font=("Segoe UI", 9, "bold"),
            bg=ColorPalette.LOSS_LIGHT,
            fg=ColorPalette.LOSS_TEXT,
            activebackground=ColorPalette.LOSS_DARK,
            activeforeground=ColorPalette.WHITE,
            relief=tk.FLAT,
            cursor="hand2",
            command=lambda: self.set_game_result(
                team, opponent, is_home,
                "away_win" if is_home else "home_win"
            )
        )
        loss_btn.pack(side=tk.LEFT, padx=2)
        
        # TIE BUTTON (Yellow)
        tie_btn = tk.Button(
            buttons_frame,
            text="T",
            width=4,
            font=("Segoe UI", 9, "bold"),
            bg=ColorPalette.TIE_LIGHT,
            fg=ColorPalette.TIE_TEXT,
            activebackground=ColorPalette.TIE_DARK,
            activeforeground=ColorPalette.WHITE,
            relief=tk.FLAT,
            cursor="hand2",
            command=lambda: self.set_game_result(team, opponent, is_home, "tie")
        )
        tie_btn.pack(side=tk.LEFT, padx=2)
        
        # Store references to buttons for later updates
        self.game_boxes[game_key] = {
            'frame': game_frame,
            'win_btn': win_btn,
            'loss_btn': loss_btn,
            'tie_btn': tie_btn
        }
    
    def create_game_key(self, team1, team2, is_home):
        """
        Create a unique identifier for a game matchup.
        
        A game key is used to uniquely identify a game for storage and lookup.
        Format: (team1, team2, "home" or "away")
        
        Args:
            team1 (str): The team playing
            team2 (str): The opponent
            is_home (bool): True if team1 is at home
            
        Returns:
            tuple: Unique game identifier (team1, team2, zone)
        """
        if is_home:
            return (team1, team2, "home")
        else:
            return (team1, team2, "away")
    
    def set_game_result(self, team, opponent, is_home, result):
        """
        Record a game prediction result and update all affected records.
        
        Clicking the same button twice toggles the prediction off.
        When a game result is set, the records for both teams are updated.
        
        Args:
            team (str): The team being predicted
            opponent (str): The opponent
            is_home (bool): True if this is a home game
            result (str): The prediction ("home_win", "away_win", or "tie")
        """
        game_key = self.create_game_key(team, opponent, is_home)
        
        # Toggle prediction off if same button is clicked again
        if self.game_results.get(game_key) == result:
            self.game_results[game_key] = None
            self.update_game_display(game_key)
            self.update_records()
            return
        
        # Store the game result
        self.game_results[game_key] = result
        
        # Update visual representation of this game
        self.update_game_display(game_key)
        
        # Recalculate all team records based on predictions
        self.update_records()
    
    def update_game_display(self, game_key):
        """
        Update the visual appearance of a game box based on its prediction.
        
        Changes the button colors to reflect the selected outcome:
        - Selected Win: Green button and background
        - Selected Loss: Red button and background
        - Selected Tie: Yellow button and background
        - Unselected: Default colors
        
        Args:
            game_key (tuple): The unique game identifier
        """
        if game_key not in self.game_boxes:
            return
        
        box = self.game_boxes[game_key]
        result = self.game_results.get(game_key)
        
        # Reset buttons to default colors
        box['win_btn'].config(bg=ColorPalette.WIN_LIGHT, fg=ColorPalette.WIN_TEXT)
        box['loss_btn'].config(bg=ColorPalette.LOSS_LIGHT, fg=ColorPalette.LOSS_TEXT)
        box['tie_btn'].config(bg=ColorPalette.TIE_LIGHT, fg=ColorPalette.TIE_TEXT)
        box['frame'].config(bg=ColorPalette.WHITE)
        
        # Apply color coding based on prediction
        if result == "home_win":
            team, opp, zone = game_key
            if zone == "home":
                # This team won at home
                box['win_btn'].config(bg=ColorPalette.WIN_DARK, fg=ColorPalette.WHITE)
                box['frame'].config(bg=ColorPalette.WIN_LIGHT)
            else:
                # This team lost away
                box['loss_btn'].config(bg=ColorPalette.LOSS_DARK, fg=ColorPalette.WHITE)
                box['frame'].config(bg=ColorPalette.LOSS_LIGHT)
                
        elif result == "away_win":
            team, opp, zone = game_key
            if zone == "away":
                # This team won away
                box['win_btn'].config(bg=ColorPalette.WIN_DARK, fg=ColorPalette.WHITE)
                box['frame'].config(bg=ColorPalette.WIN_LIGHT)
            else:
                # This team lost at home
                box['loss_btn'].config(bg=ColorPalette.LOSS_DARK, fg=ColorPalette.WHITE)
                box['frame'].config(bg=ColorPalette.LOSS_LIGHT)
                
        elif result == "tie":
            # Game ended in a tie
            box['tie_btn'].config(bg=ColorPalette.TIE_DARK, fg=ColorPalette.WHITE)
            box['frame'].config(bg=ColorPalette.TIE_LIGHT)
    
    def update_records(self):
        """
        Calculate and update team records based on all game predictions.
        
        This method:
        1. Resets all team records to 0-0-0
        2. Iterates through all predictions to recalculate records
        3. Updates all team header displays with new records
        
        When a game result is set, this ensures both teams' records are updated.
        For example: If Cowboys beat 49ers, Cowboys get +1 win, 49ers get +1 loss.
        """
        # Reset all records to 0-0-0
        self.initialize_records()
        
        # Process all game predictions and update records accordingly
        for (team1, team2, zone), result in self.game_results.items():
            if result is None:
                # Prediction has been cleared, skip it
                continue
                
            if result == "home_win":
                # Home team (team1) won, away team (team2) lost
                self.team_records[team1]["wins"] += 1
                self.team_records[team2]["losses"] += 1
                
            elif result == "away_win":
                # Away team (team1) lost, home team (team2) won
                # In this context, team1 represents the away team
                self.team_records[team1]["losses"] += 1
                self.team_records[team2]["wins"] += 1
                
            elif result == "tie":
                # Both teams get a tie
                self.team_records[team1]["ties"] += 1
                self.team_records[team2]["ties"] += 1
        
        # Update visual display of all team records in headers
        if hasattr(self, 'team_labels'):
            for team_name, button in self.team_labels.items():
                record = self.team_records[team_name]
                
                # Format record string
                record_str = (
                    f"{record['wins']}-{record['losses']}-{record['ties']}"
                    if record['ties'] > 0
                    else f"{record['wins']}-{record['losses']}"
                )
                
                # Determine arrow direction based on expansion state
                arrow = "▼" if team_name in self.expanded_teams else "▶"
                
                # Update button text with new record
                button.config(text=f"{arrow} {team_name} ({record_str})")
    
    def reset_all(self):
        """
        Clear all predictions and reset the application to initial state.
        
        Prompts user for confirmation before resetting.
        When confirmed, this will:
        1. Clear all game predictions
        2. Reset all team records to 0-0-0
        3. Reset all game button colors to default
        4. Reset all team header displays
        """
        # Ask user for confirmation to prevent accidental resets
        if messagebox.askyesno(
            "Confirm Reset",
            "Reset all predictions? This cannot be undone."
        ):
            # Clear all game predictions
            self.game_results = {}
            
            # Reset visual display of all games
            if hasattr(self, 'game_boxes'):
                for game_key in self.game_boxes.keys():
                    self.update_game_display(game_key)
            
            # Recalculate and update all records (will be 0-0-0)
            self.update_records()

# ========================
# Application Entry Point
# ========================

def main():
    """
    Application entry point.
    
    Initializes and starts the NFL Predictor application.
    Creates the root window and launches the main event loop.
    """
    # Create the root tkinter window
    root = tk.Tk()
    
    # Initialize the application
    app = NFLPredictor(root)
    
    # Start the event loop
    root.mainloop()


if __name__ == "__main__":
    main()
