import pickle
import random
import socket
import pygame
import pygame.mixer

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Load sound effect
hit_sound = pygame.mixer.Sound('ball sound.mp3')  
hit_sound.set_volume(1.0)  # Set volume to maximum

miss_sound = pygame.mixer.Sound('error.mp3')  
miss_sound.set_volume(1.0)

winning_sound = pygame.mixer.Sound('goodresult.mp3')  
winning_sound.set_volume(0.5)  

losing_sound = pygame.mixer.Sound('badresult.mp3')
losing_sound.set_volume(0.6)

# Game related global variables
WINNING_SCORE = 10
window_width = 500
window_height = 500
player1_start_x = 10
player1_start_y = 200
player2_start_x = 470
player2_start_y = 200
ball_start_x = 250
ball_start_y = 250
ball_start_velocity_x = 3
ball_start_velocity_y = 1
bat_width = 20
bat_height = 100
bat_movement_speed = 20
ball_diameter = 20

start=True

# Packet size for sending and receiving between server and clients
data_size = 4096

# FPS speed for the game clock
game_speed = 30


class PongDTO:
    """This is a data transfer object containing the variables that will be passed between server and clients."""

    # Initiate to default values
    def __init__(self):
        self.game_id = 0
        self.player_id = 0
        self.player_x = []
        self.player_y = []
        self.ball_x = 0
        self.ball_y = 0
        self.ball_velocity_x = 0
        self.ball_velocity_y = 0
        self.ball_direction_x = ''
        self.ball_direction_y = ''
        self.start_play = False
        
        self.msg = ''
        self.end_play = False
        self.points = [0, 0]
        self.hit=False
        self.checked=False
        self.miss=False
        


class Bat:
    """This class facilitates managing the players’ bats on screen."""

    def __init__(self, x, y, color):
        """Constructor to initiate the bat"""
        self.x = x
        self.y = y
        self.color = color
        self.width = bat_width
        self.height = bat_height
        self.points = 0

    def draw(self, window):
        """This method draws the bat on screen. It takes the surface as argument."""
        pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.height))

    def move(self, direction):
        """This method takes the direction of movement as argument and updates the coordinates of the bat."""
        if direction == 'up' and self.y > (bat_movement_speed / 2):
            self.y -= bat_movement_speed
        elif direction == 'down' and self.y < (window_height - bat_height - (bat_movement_speed / 2)):
            self.y += bat_movement_speed

    def add_point(self):
        """This is a data transfer object containing the variables that will be passed between server and clients."""
        self.points += 1


class Ball:
    """This class facilitates managing the movement of the ball on screen."""

    def __init__(self, x, y, color):
        """Constructor to initiate the ball"""
        
        self.x = x
        self.y = y
        self.color = color
        self.width = ball_diameter
        self.velocity_x = ball_start_velocity_x
        self.velocity_y = ball_start_velocity_y
        self.direction_x = random.choice(('positive', 'negative'))
        self.direction_y = random.choice(('positive', 'negative'))

    def draw(self, window):
        """This method draws the ball on screen. It takes the surface as argument."""
        pygame.draw.circle(window, self.color, (self.x, self.y), (ball_diameter / 2))

"""def check_collision(ball, bat):
    return (
        ball.x - ball.width // 2 < bat.x + bat.width and
        ball.x + ball.width // 2 > bat.x and
        ball.y - ball.width // 2 < bat.y + bat.height and
        ball.y + ball.width // 2 > bat.y
    )"""
    
def update_bat_ball(dto):
    """This method takes PongDTO as input and updates the positions of the bats and the ball.
    This method also sets the colours of the player and opponent differently."""

    # Set the colors of bats
    bats[player_id].color = (0, 0, 139)  # dark blue
    bats[opponent_id].color = (139, 0, 0)  # dark red

    # Set the initial coordinates of the bats and ball as received from server
    bats[0].x = dto.player_x[0]
    bats[0].y = dto.player_y[0]
    bats[1].x = dto.player_x[1]
    bats[1].y = dto.player_y[1]
    ball.x = dto.ball_x
    ball.y = dto.ball_y
    #if check_collision(ball, bats[0]) or check_collision(ball, bats[1]):
            #hit_sound.play()


# Create a socket for the server and client connection
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Server IP is where the server python file is running and listening for connections
server = "127.0.0.1"
# Port is where server is listening.
port = 5555
addr = (server, port)

# Initiate client and server connection
client.connect(addr)
# Receive the data transfer object from server for first time
receive_dto = pickle.loads(client.recv(data_size))
print("You are player ", receive_dto.player_id)
print("game id ",receive_dto.game_id)
# Retrieve the player id from the DTO
player_id = receive_dto.player_id
# The opponent id is the other id from set {0,1}
opponent_id = list({0, 1} - {receive_dto.player_id})[0]

# Initiate the Bat objects
bats = [Bat(0, 0, (0, 0, 0)), Bat(0, 0, (0, 0, 0))]
# Initiate the Ball object
ball = Ball(0, 0, (0, 0, 0))

# Update the coordinates of the bats and ball with received DTO. This will get the initial positions from the server
update_bat_ball(receive_dto)
# Initiate font
pygame.font.init()

# Show the game title on title bar of the window
pygame.display.set_caption('Ping-Pong')
# Set the surface attributes for the window
# Initialize Pygame font
pygame.font.init()
font = pygame.font.SysFont('Arial', 20)  # You can change the font and size if needed

# Set the surface attributes for the window
win = pygame.display.set_mode((window_width, window_height))

run = True
# Get the game clock
clock = pygame.time.Clock()

game_over = False
end_sound_played=False
end_sound=winning_sound
winner_text = ""
# Start the loop for the game
i=0
while run:
    # Set the game speed
    clock.tick(game_speed)
    # Fill the window color
    win.fill((173, 216, 230)) #light blue background
    if not game_over:
        # Draw the bats
        bats[0].draw(win)
        bats[1].draw(win)

        # Draw the ball
        ball.draw(win)

        # Render the updated score text
        player_score_text = font.render(f'Your score: {bats[player_id].points}', True, (0, 0, 139))  # dark blue for player
        opponent_score_text = font.render(f'Opponent: {bats[opponent_id].points}', True, (139, 0, 0))  # darl red for opponent

        # Blit (draw) the text onto the game window at the top
        if player_id==0 :
            win.blit(player_score_text, (50, 10))  # Adjust position (50, 10) as needed
            win.blit(opponent_score_text, (window_width - 150, 10))  # Adjust position to fit the window width
        else :
            win.blit(opponent_score_text, (50, 10))  # Adjust position (50, 10) as needed
            win.blit(player_score_text, (window_width - 150, 10))  # Adjust position to fit the window width
        
              
         
        #winning criteria    
        if bats[player_id].points >= WINNING_SCORE:
            game_over = True
            winner_text = "You won :)"
            end_sound=winning_sound
        elif bats[opponent_id].points >= WINNING_SCORE:
            game_over = True
            winner_text = "You lost :("     
            #end_sound=losing_sound 
    if game_over:
        # Display the winner message
        win.fill((173, 216, 230))  # Optional: Clear the screen
        winner_message = font.render(winner_text, True, (10, 83, 10))  
        win.blit(winner_message, (window_width // 2 -50, window_height // 2))
        
        pygame.display.update()
        if not end_sound_played:
            end_sound.play()
            end_sound_played=True
        for i in range(5, 0, -1):
            pygame.time.delay(1000) 
        pygame.quit()
        break    
        
                
    
                    

    
    # Render the window elements
    #pygame.display.update()

    # Check for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        # Get the list of keys pressed
        keys = pygame.key.get_pressed()
        # Break the loop if player has escaped the game
        if keys[pygame.K_ESCAPE]:
            run = False
        # ‘W’ to move player’s bat upwards
        if keys[pygame.K_w]: #or keys[pygame.K_UP]:
            bats[player_id].move('up')
        # ‘S’ to move player’s bat downwards
        if keys[pygame.K_s]:# or keys[pygame.K_DOWN]:
            bats[player_id].move('down')
        # Break the loop if player has clicked on the window
        if event.type == pygame.MOUSEBUTTONDOWN:
            run = False

    # Set the DTO as per screen for both players. This is required for opponent because
    # client should reflect what is received
    receive_dto.player_y[0] = bats[0].y
    receive_dto.player_y[1] = bats[1].y

    try:
        # Send the DTO to server
        client.sendall(pickle.dumps(receive_dto))
        # Receive the DTO from server
        receive_dto = pickle.loads(client.recv(data_size))
    # Break loop for any exception
    except Exception as e:
        run = False
        print("Couldn't get game")
        print("An error occurred:", e)
        break
    if receive_dto.hit:
        hit_sound.play()
    if receive_dto.miss:
        miss_sound.play()   
    #display waiting for game message
    if receive_dto.start_play==False :
        waiting_text = font.render('Waiting for opponent', True, (10, 83, 10))
        win.blit(waiting_text, ((window_width/2 -80), 80))
        
    #countdown before game starts    
    if receive_dto.start_play and start:
        text_x, text_y = (window_width / 2 - 80), 80
        text_width, text_height = 200, 40 
        for i in range(3, 0, -1):
            pygame.draw.rect(win, (173, 216, 230), (text_x, text_y, text_width, text_height))
            starting_text = font.render(f'Game starts in {i}..', True, (10, 83, 10))
            win.blit(starting_text, ((window_width / 2 - 80), 80))
            pygame.display.update()
            pygame.time.delay(1000) 
        pygame.draw.rect(win, (173, 216, 230), (text_x, text_y, text_width, text_height))  # Clear the area
        go_text = font.render('Go!', True, (10, 83, 10))
        win.blit(go_text, (window_width/2-50, text_y))
        pygame.display.update()
        pygame.time.delay(250)    
        start=False
            
            
    pygame.display.update()
    # Update the coordinates of the bats and ball with received DTO.
    update_bat_ball(receive_dto)
    

    # Update the points as received from DTO into the bat objects
    bats[player_id].points = receive_dto.points[player_id]
    bats[opponent_id].points = receive_dto.points[opponent_id]
        

