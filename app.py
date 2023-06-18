from flask import Flask, render_template, redirect, url_for, request, session
import mysql.connector, random, datetime

# TODO: lots of error checking, improved algorithm, websockets, google auth, payment integration, image rec chip counter, overhaul ui later

# Initialize Flask instance
app = Flask(__name__)
app.secret_key = 'phase3_secret_key'

# Configure MySQL connection
db = mysql.connector.connect(
    host="127.0.0.1",               # MySQL server hostname
    user="root",                    # MySQL username
    password="5BJhs_SS9Bb9#uYz",    # MySQL password
    database="poker"                # MySQL database name
)
cursor = db.cursor()

# Route for the index page
@app.route('/')
def index():
    # Render the index page template
    return render_template('login.html')
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Render login page
    if request.method == 'GET':
        return render_template('login.html')
    
    # Try to log in the user
    if request.method == 'POST':

      # Get form data
      username = request.form['username']
      password = request.form['password']

      # Check for credentials in the database
      cursor.execute("SELECT * FROM player WHERE username = %s AND password = %s", (username, password))
      player = cursor.fetchone()

      # If credentials are valid, store the users ID/Username and redirect to the join page
      if player:
          session['player_id'] = player[0]
          session['username'] = player[1]
          return redirect('/join')

      # Otherwise, render the login page again
      error = 'Incorrect username or password. Please try again.'
      return render_template('login.html', error=error)

@app.route('/logout', methods=['GET'])
def logout():
    # Clear the session data and redirect to the login page
    session.clear()
    return redirect('/login')

# Route for the create user page
@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    # Render the create user page
    if request.method == 'GET':
      return render_template('create_user.html')

    # Try to create the user
    if request.method == 'POST':
        # Get form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if any of the fields are blank
        if not all([first_name, last_name, username, password]):
            error = "Please fill in all fields."
            return render_template('create_user.html', error=error)

        # Check if username already exists in the database
        cursor.execute("SELECT * FROM player WHERE username = %s", (username,))
        player = cursor.fetchone()

        # If username exits, let the user try again
        if player:
            error = "Username already exists. Please choose a different one."
            return render_template('create_user.html', error=error)

        # Otherwise add the user to the database
        cursor.execute("INSERT INTO player (Player_id, First_name, Last_name, Username, Password) VALUES (%s, %s, %s, %s, %s)",
                            (str(generate_id(9)), first_name, last_name, username, password))
        db.commit()
        return render_template('login.html')

# Route for the join page
@app.route('/join', methods=['GET', 'POST'])
def join():
    # Render the join game page
    if request.method == 'GET':
      return render_template('join.html')
    
    # Try to add the user to the game
    if request.method == 'POST':
        # Get input from join page
        join_code = request.form['join_code']
        player_id = session['player_id']

        # Check if the game code is valid
        cursor.execute("SELECT * FROM game WHERE Join_code = %s", (join_code,))
        game = cursor.fetchone()
        
        # If code is invalid, let user try again
        if not game:
            error = 'Invalid game code. Please try again.'
            return render_template('join.html', error=error)
        
        # Check that game has less than 9 players
        game_id = game[0]
        cursor.execute("SELECT COUNT(*) FROM participates_in WHERE Game_id = %s", (game_id,))
        player_count = cursor.fetchone()[0]
        if player_count == 9:
            error = 'The game you are trying to join is full.'
            return render_template('join.html', error=error)
        
        # Look for player in the current game
        cursor.execute("SELECT * FROM participates_in WHERE Player_id = %s AND Game_id = %s", (player_id, game_id))

        # If the player has previously joined the game, update their status to currently playing
        if cursor.fetchone():
            cursor.execute("UPDATE participates_in SET Currently_playing = 1 WHERE Player_id = %s and Game_id = %s", (player_id, game_id))
            db.commit()

        # Otherwise, add them to the game and increment their Games_played metric
        else:
            cursor.execute("INSERT INTO participates_in (Player_id, Game_id, Currently_playing) VALUES (%s, %s, %s)", (player_id, game_id, 1))
            db.commit()

            cursor.execute("UPDATE player SET Games_played = Games_played + 1 WHERE Player_id = %s", (player_id,))
            db.commit()

        # Redirect the player to the game page
        return redirect(url_for('game', game_id=game_id, game_name=game[1]))

# Route for the game page
@app.route('/game/<game_id>/<game_name>', methods=['GET', 'POST'])
def game(game_id, game_name):
    # Retrieve join code from database
    cursor.execute("SELECT Join_code FROM game WHERE Game_id = %s", (game_id,))
    join_code = cursor.fetchone()[0]

    # Retrieve list of players participating in the game from database
    cursor.execute("SELECT player.Username FROM player JOIN participates_in ON player.Player_id = participates_in.Player_id WHERE participates_in.Game_id = %s AND participates_in.Currently_playing = 1", (game_id,))
    players = cursor.fetchall()
    players = [player[0] for player in players]

    # Retrieve buy-in amount
    player_id = session.get('player_id')

    cursor.execute("SELECT Buyin_amount, Cashout_amount FROM participates_in WHERE Player_id = %s AND Game_id = %s", (player_id, game_id))
    buyin_amount, cashout_amount = cursor.fetchone()
    buyin_amount = "{:.2f}".format(float(buyin_amount))
    cashout_amount = "{:.2f}".format(float(cashout_amount))

    # Retrieve chip values
    cursor.execute("SELECT Green_chips_value, White_chips_value, Red_chips_value, Blue_chips_value, Black_chips_value FROM chip_case WHERE Game_id = %s", (game_id,))
    chip_values = cursor.fetchone()

    # Format chip values
    chip_dict = {
        'Green': '${:,.2f}'.format(float(chip_values[0])),
        'White': '${:,.2f}'.format(float(chip_values[1])),
        'Red': '${:,.2f}'.format(float(chip_values[2])),
        'Blue': '${:,.2f}'.format(float(chip_values[3])),
        'Black': '${:,.2f}'.format(float(chip_values[4]))
    }

    chip_values_text = '  '.join(f"{color}: {value}" for color, value in sorted(chip_dict.items(), key=lambda x: x[1], reverse=True))

    # Render the game page
    return render_template(
        'game.html',
        game_id=game_id,
        game_name=game_name,
        join_code=join_code,
        username=session.get('username'),
        players=players,
        buyin_amount=buyin_amount,
        cashout_amount=cashout_amount,
        chip_values_text=chip_values_text
    )

# Route for the create game page
@app.route('/create_game', methods=['GET', 'POST'])
def create_game():

    # Render the create game page
    if request.method == 'GET':
        join_code = generate_id(5)
        game_id = generate_id(9)

        return render_template('create_game.html', join_code=join_code, game_id=game_id)
    
    if request.method == 'POST':

        # Add game to database
        game_id = request.form['game_id']
        game_name = request.form['game_name']        
        join_code = request.form['join_code']
        date = datetime.datetime.now().strftime('%Y-%m-%d')
        start_time = datetime.datetime.now().strftime('%H:%M:%S')
        stakes = request.form['stakes-dropdown']
        small_blind = float(stakes.split('/')[0])
        big_blind = float(stakes.split('/')[1])
        min_buyin = small_blind * 40
        max_buyin = big_blind * 100

        cursor.execute("INSERT INTO game (Game_id, Game_name, Join_code, Date, Start_time, Min_buyin, Max_buyin, Small_blind, Big_blind) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (game_id, game_name, join_code, date, start_time, min_buyin, max_buyin, small_blind, big_blind))
        db.commit()

        # Add host to database
        player_id = session['player_id']
        cursor.execute("SELECT * FROM player WHERE Player_id = %s", (player_id,))
        player_data = cursor.fetchone()
        host_id = player_id
        first_name = player_data[1]
        last_name = player_data[2]

        cursor.execute("INSERT INTO host (Host_id, Game_id, First_name, Last_name) VALUES (%s, %s, %s, %s)", (host_id, game_id, first_name, last_name))
        db.commit()

        # Add host to game
        player_id = session['player_id']
        game_id = game_id

        cursor.execute("INSERT INTO participates_in (Player_id, Game_id, Currently_playing) VALUES (%s, %s, %s)", (player_id, game_id, 1))
        db.commit()

        # Update hosts Games_played metric
        cursor.execute("UPDATE player SET Games_played = Games_played + 1 WHERE Player_id = %s", (player_id,))
        db.commit()

        # Add prize pool to database
        pool_id = generate_id(9)
        cursor.execute("INSERT INTO prize_pool (Pool_id, Game_id) VALUES (%s, %s)",
                                               (pool_id, game_id))
        db.commit()

        # Add chip case to database
        green_count = int(request.form['green_chips'])
        white_count = int(request.form['white_chips'])
        red_count = int(request.form['red_chips'])
        blue_count= int(request.form['blue_chips'])
        black_count = int(request.form['black_chips'])

        chip_values = get_chip_values(big_blind, green_count, white_count, red_count, blue_count, black_count)
        
        green_value = chip_values.get('green', 0)
        white_value = chip_values.get('white', 0)
        red_value = chip_values.get('red', 0)
        blue_value = chip_values.get('blue', 0)
        black_value = chip_values.get('black', 0)

        current_value = green_value * green_count + white_value * white_count + red_value * red_count + blue_value * blue_count + black_value * black_count;

        cursor.execute("INSERT INTO chip_case (Case_id, Game_id, Current_value, Green_chips_amount, Green_chips_value, White_chips_amount, White_chips_value, Red_chips_amount, Red_chips_value, Blue_chips_amount, Blue_chips_value, Black_chips_amount, Black_chips_value) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (generate_id(9), game_id, current_value, green_count, green_value, white_count, white_value, red_count, red_value, blue_count, blue_value, black_count, black_value))
        db.commit()

        return redirect(url_for('game', game_id=game_id, game_name=game_name))

# Route for exiting a game
@app.route('/exit', methods=['POST'])
def exit():
    # Get form data
    game_id = request.form['game_id']
    game_name = request.form['game_name']
    player_id = session['player_id']
    
    # Check that user has cashed out of the game before exiting
    db.commit()
    cursor.execute("SELECT Num_buyins, Num_cashouts FROM participates_in where Player_id = %s AND Game_id = %s", (player_id, game_id)) 
    buyin_data = cursor.fetchall()

    num_buyins = int(buyin_data[0][0])
    num_cashouts = int(buyin_data[0][1])
    has_cashed_out = num_buyins == num_cashouts

    # If user has not cashed out, redirect to game page
    if (not has_cashed_out):
        session['cashout_error'] = "Please cashout before exiting"
        return redirect(url_for('game', game_id=game_id, game_name=game_name))
    
    # Check if the user is the host of the game
    cursor.execute("SELECT * FROM host WHERE Host_id = %s AND Game_id = %s", (player_id, game_id))
    host_data = cursor.fetchone()
    
    # Reset host error
    session.pop('host_error', None)

    # If the user is the host
    if host_data:

        # Check that all other players have left the game before the host
        cursor.execute("SELECT COUNT(*) FROM participates_in WHERE game_id = %s AND currently_playing = 1", (game_id,))
        players_remaining = cursor.fetchone()[0] - 1
        if (players_remaining > 0):
            session['host_error'] = "The game host must exit last. Players remaining: " + str(players_remaining)
            return redirect(url_for('game', game_id=game_id, game_name=game_name))
        
        # Get list of players and their buyin data
        cursor.execute("SELECT Player_id, Buyin_amount, Cashout_amount FROM participates_in WHERE Game_id = %s", (game_id,))
        results = cursor.fetchall()

        formatted_data = {row[0]: (float(row[1]), float(row[2])) for row in results}

        # Calculate all debts from the game and insert into database
        debts = calculate_debt(formatted_data)
        for creditor_id, debt_data in debts.items():
            for debt_entry in debt_data:
                debtor_id = debt_entry[0]
                debt_amount = debt_entry[1]
                current_date = datetime.datetime.now().strftime('%Y-%m-%d')
                current_time = datetime.datetime.now().strftime('%H:%M:%S')
                cursor.execute("INSERT INTO debt (Debt_id, Debtor_id, Creditor_id, Debt_amount, Date_created, Time_created) VALUES (%s, %s, %s, %s, %s, %s)", (generate_id(9), debtor_id, creditor_id, debt_amount, current_date, current_time))
                db.commit()

        # Update metrics in the player table: Games_won, Games_lost, Total_debt
        for result in results:
            temp_player_id = result[0]
            buyin_amount = float(result[1])
            cashout_amount = float(result[2])

            if cashout_amount >= buyin_amount:
                cursor.execute("UPDATE player SET Games_won = Games_won + 1 WHERE Player_id = %s", (temp_player_id,))
            else:
                cursor.execute("UPDATE player SET Games_lost = Games_lost + 1 WHERE Player_id = %s", (temp_player_id,))

            cursor.execute("UPDATE player SET Total_debt = Total_debt - %s WHERE Player_id = %s", (cashout_amount - buyin_amount, temp_player_id))
            db.commit()

        # Remove users from participates_in
        cursor.execute("DELETE FROM participates_in WHERE Game_id = %s", (game_id,))
        db.commit()

        # Remove the host from the database
        cursor.execute("DELETE FROM host WHERE Host_id = %s AND Game_id = %s", (player_id, game_id))
        db.commit()

        # Remove the prize_pool from the database
        cursor.execute("DELETE FROM prize_pool WHERE Game_id = %s", (game_id,))
        db.commit()

        # Remove the chip_case from the database
        cursor.execute("DELETE FROM chip_case WHERE Game_id = %s", (game_id,))
        db.commit()

        # Remove the game from the database
        cursor.execute("DELETE FROM game WHERE Game_id = %s", (game_id,))
        db.commit()
    
    # Update users currently_playing status to false
    cursor.execute("UPDATE participates_in SET Currently_playing = 0 WHERE Player_id = %s and Game_id = %s", (player_id, game_id))
    db.commit()

    # Redirect user to the join page
    return render_template('join.html')


# Route for the profile page
@app.route('/profile', methods=['GET'])
def profile():

    # Get username from the database
    cursor.execute("SELECT username FROM player WHERE player_id = %s", (session['player_id'],))
    result = cursor.fetchone()
    username = result[0]

    # Redirect to the users profile page
    return render_template('profile.html', username=username, player_id=session['player_id'])

# Route for the stats page
@app.route('/stats', methods=['GET'])
def stats():
    # Get the users ID
    player_id = session.get('player_id')
    
    # Get the user from the database
    cursor.execute("SELECT First_name, Last_name, Games_played, Games_won, Games_lost, Total_debt, Total_buyin_amount, Total_cashout_amount, Win_percentage, Earnings_per_buyin FROM player WHERE player_id = %s", (player_id,))
    player_data = cursor.fetchone()
    
    # Redirect to statistics page
    return render_template('stats.html', player_data=player_data)

# Route for the history page
@app.route('/history', methods=['GET'])
def history():
    # Render the history page
    return render_template('history.html')

# Route for the buyin page
@app.route('/buyin', methods=['POST'])
def buyin():
    # Get form data
    game_id = request.form['game_id']
    game_name = request.form['game_name']
    
    # Get stakes data from the database for buyin UI
    cursor.execute("SELECT Min_buyin, Max_buyin FROM game WHERE Game_id = %s", (game_id,))
    result = cursor.fetchone()
    min_buyin = result[0]
    max_buyin = result[1]

    # Redirect to the buyin page
    return render_template('buyin.html', game_id=game_id, game_name=game_name, min_buyin=min_buyin, max_buyin=max_buyin)

# Route for the submit_buyin page
@app.route('/submit_buyin', methods=['POST'])
def submit_buyin():
    # Get form data
    game_id = request.form['game_id']
    game_name = request.form['game_name']
    min_buyin = request.form['min_buyin']
    max_buyin = request.form['max_buyin']
    input_buyin_amount = request.form['buyin_amount']
    player_id = session['player_id']

    # Get player data from database
    db.commit()
    cursor.execute("SELECT Num_buyins, Num_cashouts FROM participates_in where Player_id = %s AND Game_id = %s", (player_id, game_id)) 
    buyin_data = cursor.fetchall()
    num_buyins = int(buyin_data[0][0])
    num_cashouts = int(buyin_data[0][1])
    is_bought_in = num_buyins > num_cashouts
    
    # If user has already bought in, make them cash out
    if (is_bought_in):
        error = "You are bought in to this game. If you want to re-buy, please cashout first."
        return render_template('buyin.html', game_id=game_id, game_name=game_name, min_buyin=min_buyin, max_buyin=max_buyin, error=error)
    
    # Check if buyin amount is within range
    if (not input_buyin_amount or float(input_buyin_amount) < float(min_buyin)) or (float(input_buyin_amount) > float(max_buyin)):
        error = 'Invalid buy-in amount for this game.'
        return render_template('buyin.html', game_id=game_id, game_name=game_name, min_buyin=min_buyin, max_buyin=max_buyin, error=error)
    
    # Update Buyin_amount in the participates_in table
    cursor.execute("UPDATE participates_in SET Buyin_amount = Buyin_amount + %s, Num_buyins = Num_buyins + 1 WHERE Player_id = %s AND Game_id = %s", (input_buyin_amount, player_id, game_id))
    db.commit()

    # Update Total_value in the prize_pool table
    cursor.execute("UPDATE prize_pool SET Total_value = Total_value + %s WHERE Game_id = %s", (input_buyin_amount, game_id))
    db.commit()

    # Update Current_value in the chip_case table
    cursor.execute("UPDATE chip_case SET Current_value = Current_value - %s WHERE Game_id = %s", (input_buyin_amount, game_id))
    db.commit()

    # Update player metrics for total_buyin_amount
    cursor.execute("UPDATE player SET Total_buyin_amount = Total_buyin_amount + %s WHERE Player_id = %s", (input_buyin_amount, player_id))
    db.commit()

    # TODO: Deal with chips (at later time when feature is implemented)

    # Redirect to the game page
    return redirect(url_for('game', game_id=game_id, game_name=game_name))

# Route for the cashout page
@app.route('/cashout', methods=['POST'])
def cashout():
    # Get form data
    game_id = request.form['game_id']
    game_name = request.form['game_name']
    
    # Redirect to the cashout page
    return render_template('cashout.html', game_id=game_id, game_name=game_name)

# Route for the submit_cashout page
@app.route('/submit_cashout', methods=['POST'])
def submit_cashout():
    # Get form data
    game_id = request.form['game_id']
    game_name = request.form['game_name']
    player_id = session['player_id']

    # Get player data from database
    db.commit()
    cursor.execute("SELECT Num_buyins, Num_cashouts FROM participates_in where Player_id = %s AND Game_id = %s", (player_id, game_id)) 
    buyin_data = cursor.fetchall()
    num_buyins = int(buyin_data[0][0])
    num_cashouts = int(buyin_data[0][1])
    is_bought_in = num_buyins > num_cashouts

    # Check that user has bought in before cashing out
    if (not is_bought_in):
        error = "Please buy in to the game before cashing out."
        return render_template('cashout.html', game_id=game_id, game_name=game_name, error=error)
    
    # Calculate cashout value based on users chips
    green = request.form.get('green_chips') or 0
    white = request.form.get('white_chips') or 0
    red = request.form.get('red_chips') or 0
    blue = request.form.get('blue_chips') or 0
    black = request.form.get('black_chips') or 0

    # Get chip values from database
    cursor.execute("SELECT Green_chips_value, White_chips_value, Red_chips_value, Blue_chips_value, Black_chips_value FROM chip_case WHERE Game_id = %s", (game_id,))
    chip_values = cursor.fetchone()

    green_value = float(chip_values[0])
    white_value = float(chip_values[1])
    red_value = float(chip_values[2])
    blue_value = float(chip_values[3])
    black_value = float(chip_values[4])

    # Calculate cashout amount from chips
    cashout_amount = float(green) * green_value + float(white) * white_value + float(red) * red_value + float(blue) * blue_value + float(black) * black_value

    # Update Buyin_amount in the participates_in table
    cursor.execute("UPDATE participates_in SET Cashout_amount = Cashout_amount + %s, Num_cashouts = Num_cashouts + 1 WHERE Player_id = %s AND Game_id = %s", (cashout_amount, player_id, game_id))
    db.commit()

    # Update Total_value in the prize_pool table
    cursor.execute("UPDATE prize_pool SET Total_value = Total_value - %s WHERE Game_id = %s", (cashout_amount, game_id))
    db.commit()

    # Update Current_value in the chip_case table
    cursor.execute("UPDATE chip_case SET Current_value = Current_value + %s WHERE Game_id = %s", (cashout_amount, game_id))
    db.commit()

    # Update player metrics: total_cashout_amount
    cursor.execute("UPDATE player SET Total_cashout_amount = Total_cashout_amount + %s WHERE Player_id = %s", (cashout_amount, player_id))
    db.commit()

    # Reset cashout error
    session.pop('cashout_error', None)

    # Redirect to game page
    return redirect(url_for('game', game_id=game_id, game_name=game_name))

# Route for the debt page
@app.route('/debt', methods=['GET'])
def debt():
    # Get ID from session
    player_id = session['player_id']

    # Get debt data from database
    cursor.execute("SELECT Debt_id, Debtor_id, Creditor_id, Debt_amount, Date_created, Time_created FROM debt WHERE Debtor_id = %s OR Creditor_id = %s", (player_id, player_id))
    rows = cursor.fetchall()

    # Create list of strings to display debts in the form: {debtor_name} owes you ${debt_amount} [{date}]
    debts = []
    for row in sorted(rows, key=lambda x: (x[4], x[5])):
        debtor_id = row[1]
        creditor_id = row[2]
        debt_amount = row[3]
        date_created = row[4]

        if debtor_id == player_id:
            cursor.execute("SELECT First_name, Last_name FROM player WHERE Player_id = %s", (creditor_id,))
            creditor_name = cursor.fetchone()
            creditor_name = f"{creditor_name[1]}, {creditor_name[0]}"
            debt_str = f"You owe {creditor_name} ${debt_amount:.2f} [{date_created}]"
        elif creditor_id == player_id:
            cursor.execute("SELECT First_name, Last_name FROM player WHERE Player_id = %s", (debtor_id,))
            debtor_name = cursor.fetchone()
            debtor_name = f"{debtor_name[1]}, {debtor_name[0]}"
            debt_str = f"{debtor_name} owes you ${debt_amount:.2f} [{date_created}]"
        debts.append(debt_str)

    # Redirect to debt page
    return render_template('debt.html', debts=debts)

# Route for the delete_account page
@app.route('/delete_account', methods=['GET', 'POST'])
def delete_account():
    # Get ID from session
    player_id = request.form['player_id']

    # Remove account from database
    cursor.execute("DELETE FROM player WHERE Player_id = %s", (player_id,))
    db.commit()
    
    # Redirect to the login page
    return render_template('login.html')

# Generates random id of specified length in digits
def generate_id(length):
    return random.randint(10**(length-1), 10**length-1)

# Determines the value of each chip based on the big blind value and the number of each color chip available
# For example, if the big blind is $0.05 and there are 50 of each chip color, the function will return
# Red: $1.00  White: $0.25  Blue: $0.25  Green: $0.05  Black: $0.01
def get_chip_values(big_blind, green, white, red, blue, black):
    # Define the possible chip values in descending order
    valid_chip_values = [100, 25, 5, 1, 0.25, 0.05, 0.01]

    # Calculate the minimum total chip amount for a 9 player game
    game_buyin = 9 * 100 * big_blind
    max_buyin = 100 * big_blind

    # Find the biggest chip value less than or equal to the max_buyin
    max_chip_value = 0
    for chip_value in valid_chip_values:
        if chip_value > max_chip_value and chip_value < max_buyin:
            max_chip_value = chip_value

    # Select which 4 chip values will be used for this game
    used_values = valid_chip_values[valid_chip_values.index(max_chip_value):]
    used_values = used_values[0:4]

    # Order chip colors by their count in decending order
    chip_counts = [(color, count) for color, count in [("green", green), ("white", white), ("red", red), ("blue", blue), ("black", black)] if count > 0]
    chip_counts.sort(reverse=True, key=lambda x: x[1])

    # Assign each chip color a value
    values = {}
    for i, (color, count) in enumerate(chip_counts):
        # The most chips should have the second least value
        if i == 0:
            values[color] = used_values[-2]
        # The least chips should have the least value
        elif i == len(chip_counts)-1:
            values[color] = used_values[-1]
        # The second least chips should have the greatest value
        elif i == len(used_values)-2:
            values[color] = used_values[0]
        else:
            values[color] = used_values[1]

    # Check if the total value of all chips is greater than the game_buyin
    total_value = sum(values[color] * count for color, count in chip_counts)
    if total_value > game_buyin:
        return values
    else:
        # TODO: resolve this error
        return {"green": "-1"}

def calculate_debt(input):
    # Calculate the total buyin and cashout amounts
    total_buyin = sum([amounts[0] for amounts in input.values()])
    total_cashout = sum([amounts[1] for amounts in input.values()])
    
    # Check for impossible debt scenarios i.e. 1 player only
    if len(input) < 2 or total_buyin == 0:
        return {}
    
    # Calculate the amount owed to each player
    # Distribute the difference between the total cashout and total buyin amounts
    # proportionally among the players based on their individual contributions to
    # the total buyin amount
    amount_owed = {}
    for id, amounts in input.items():
        buyin_amount = amounts[0]
        cashout_amount = amounts[1]
        buyin_fraction = buyin_amount / total_buyin
        owed_amount = (cashout_amount - buyin_amount) + ((total_cashout - total_buyin) * buyin_fraction)
        amount_owed[id] = owed_amount

    # Find the players who owe money and those who are owed money
    players_owed = {id: amount for id, amount in amount_owed.items() if amount > 0}
    players_owing = {id: -amount for id, amount in amount_owed.items() if amount < 0}
    
    # First look for players who owe/are owed equal amounts and add them to the output since they cancel each other out
    output={}
    players_owed_copy = players_owed.copy()  # create a copy of players_owed
    for owed_player, owed_amount in players_owed_copy.items():
        for owing_player, owing_amount in players_owing.items():
            if owed_amount == owing_amount:
                output[owed_player] = [(owing_player, owed_amount)]
                del players_owed[owed_player]
                del players_owing[owing_player]
                break
   
    # Iterate through remaining players in players_owed and players_owing
    # For each player owing, assign debts to players owed until they have reached the amount they owe. 
    for owing_player, owing_amount in players_owing.items():
        while owing_amount > 0:
            for owed_player, owed_amount in players_owed.items():
                if owing_amount >= owed_amount:
                    output.setdefault(owed_player, []).append((owing_player, owed_amount))
                    owing_amount -= owed_amount
                    del players_owed[owed_player]
                    break
                else:
                    output.setdefault(owed_player, []).append((owing_player, owing_amount))
                    players_owed[owed_player] -= owing_amount
                    owing_amount = 0
                    break
    output = {player: [(other_player, round(amount, 2)) for other_player, amount in debts] for player, debts in output.items()}

    return output

if __name__ == '__main__':
    app.run(debug=True)