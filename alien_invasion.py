import sys
import json

import pygame

from time import sleep

from settings import Settings
#need to import ship
from ship import Ship

from bullet import Bullet

from alien import Alien
from game_stats import GameStats
from button import Button
from scoreboard import Scoreboard

class AlienInvasion:

    def __init__(self):
        pygame.init()

        self.settings=Settings()

        self.screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height

        self.screen= pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height)
        )
        
        pygame.display.set_caption("Alien Invasion")

        # Create an instance to store game statistics
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)
        
        self.ship=Ship(self)
        self.bullets = pygame.sprite.Group()

        self.aliens= pygame.sprite.Group()
        
        self._create_fleet()

        # Make the play button
        self.play_button = Button(self,self.screen,'Play')

        # Make diffuculty level buttons
        self._make_difficulty_buttons()


        #set background color
        #self.bg_color=(230,230,230)
    
    def _make_difficulty_buttons(self):
        '''Make buttons that allow player to select difficulty level'''
        self.easy_button = Button(self, self.screen, 'Easy')
        self.medium_button = Button(self,self.screen, 'Medium')
        self.difficult_button = Button(self,self.screen, 'Difficult')


        # Position buttons so they don't overlap
        self.easy_button.rect.top = (
        self.play_button.rect.top + 1.5*self.play_button.rect.height)
        self.easy_button._update_msg_position()

        self.medium_button.rect.top = (
        self.easy_button.rect.top + 1.5*self.easy_button.rect.height)
        self.medium_button._update_msg_position()

        self.difficult_button.rect.top = (self.medium_button.rect.top + 1.5*self.medium_button.rect.height)
        self.difficult_button._update_msg_position()

    def run_game(self):
        while True:
            self._check_events()            
            
            if self.stats.game_active:
                self.ship.update()                                    
                self._update_bullets()
                self._update_aliens()
            
            self._update_screen()
    

    def _create_fleet(self):
        '''Create the fleet of aliens'''
        # Make an Alien
        alien = Alien(self)
        alien_width, alien_height=alien.rect.size
        available_space_x = self.settings.screen_width - (2*alien_width)
        number_aliens_x=available_space_x//(2*alien_width)

        # Determine the number of rows of aliens that fit on the screen
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height - (3*alien_height)-ship_height)

        number_rows = available_space_y//(2*alien_height)

        # Create the full fleet of aliens
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)
    

    def _create_alien(self, alien_number, row_number):
        # Create an alien and place it in the row
        alien=Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2*alien_width*alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2* alien.rect.height* row_number
        
        self.aliens.add(alien)
    
    def _check_fleet_edges(self):
        '''Respond appropiately if any aliens have reached an edge'''
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break
    
    def _change_fleet_direction(self):
        '''Drop the entire fleet and change the fleet's direction'''
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1
    
    def _ship_hit(self):
        '''Respond to the ship being hit by an alien'''
        if self.stats.ships_left > 0:
            #Decrement ships_left and update scoreboard
            self.stats.ships_left -= 1
            self.sb.prep_ships()
            

            # Get rid of any remaining aliens and bullets
            self.aliens.empty()
            self.aliens.empty()

            # Create a new fleet and center the ship
            self._create_fleet()
            self.ship.center_ship()

            # Pause
            sleep(0.5)
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

            
    def _check_events(self):
        #Responds to keypresses and mouse events
        for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    sys.exit()
                elif event.type==pygame.KEYDOWN:
                    self._check_keydown_events(event)

                elif event.type==pygame.KEYUP:
                    self._check_keyup_events(event)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    self._check_play_button(mouse_pos)
                    self._check_difficulty_buttons(mouse_pos)
    
    def _check_play_button(self, mouse_pos):
        '''Start a new game when the player clicks play'''
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
           # Reset the game settings
           self.settings.initialize_dynamic_settings()
           self._start_game()
           self.sb.prep_score()
           self.sb.prep_level()
           self.sb.prep_ships()
    
    def _check_difficulty_buttons(self, mouse_pos):
        '''Set the appropiate difficulty level'''
        easy_button_clicked = self.easy_button.rect.collidepoint(mouse_pos)
        medium_button_clicked = self.medium_button.rect.collidepoint(mouse_pos)
        diff_button_clicked = self.difficult_button.rect.collidepoint(mouse_pos)

        if easy_button_clicked:
            self.settings.difficulty_level = 'easy'
        elif medium_button_clicked:
            self.settings.difficulty_level = 'medium'
        elif diff_button_clicked:
            self.settings.difficulty_level = 'difficult'
        
    

    def _start_game(self):
        '''Start a new Game'''
        # Reset the game statistics
        self.stats.reset_stats()
        self.stats.game_active = True

        # Get rid of any remaining aliens and bullets
        self.aliens.empty()
        self.bullets.empty()

        # Create a new fleet an center the ship
        self._create_fleet()
        self.ship.center_ship()

        # Hide the mouse cursor
        pygame.mouse.set_visible(False)


    def _check_keydown_events(self, event):
        '''Respond to keypresses'''
        if event.key==pygame.K_RIGHT:          
            self.ship.moving_right=True
        elif event.key==pygame.K_LEFT:
            self.ship.moving_left=True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
        elif event.key == pygame.K_p and not self.stats.game_active:
            self._start_game()
    
    def _check_keyup_events(self, event):
        '''Respond to Key Releases'''
        if event.key==pygame.K_RIGHT:
            self.ship.moving_right=False
        elif event.key==pygame.K_LEFT:
            self.ship.moving_left=False
        
    
    def _fire_bullet(self):
        '''Create a new bullet and add it to the bullets group'''
        
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet=Bullet(self)
            self.bullets.add(new_bullet)
    
    def _update_bullets(self):
        '''Update position of bullets and get rid of old bullets'''
        self.bullets.update()

            # Get rid of bullets that have disappeared
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        
        self._check_bullet_alien_collisions()
    
    def _check_bullet_alien_collisions(self):
        ''' Respond to bullet-alien collisions'''
        # Check for any bullets that have hit aliens.
        # if so, get rid of the alien and the bullet
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)

        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points
            self.sb.prep_score()
            self.sb.check_high_score()

        if not self.aliens:
            # Destroy existing bullets and create new fleet.
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

            # Increase level
            self.stats.level += 1
            self.sb.prep_level()
    
    def _check_aliens_bottom(self):
        '''Check if any aliens have reached the bottom of the screen'''
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # Treat this the same as if the ship got hit
                self._ship_hit()
                break

    def _update_aliens(self):
        '''Check if trhe fleet is at an edge then update the positions of all aliens in the fleet'''
        
        self._check_fleet_edges()
        self.aliens.update()

        # Look for alien - shi collisions
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()
        
        # look for aliens hitting the bottom of the screen
        self._check_aliens_bottom()

    def _update_screen(self):
        '''update images on the screen, and flip to the new screen'''
        #Redraw the screen during each pass through the loop
        self.screen.fill(self.settings.bg_color)
            
        #to draw the ship on the screen
        self.ship.blitme()

        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        
        self.aliens.draw(self.screen)
        self.sb.show_score()

        # Draw the play button if the game is inactive
        if not self.stats.game_active:
            self.play_button.draw_button()
            self.easy_button.draw_button()
            self.medium_button.draw_button()
            self.difficult_button.draw_button()

        pygame.display.flip()
    
    def _close_game(self):
        '''Save high score and exit'''
        saved_high_score = self.stats.get_saved_high_score()
        if self.stats.high_score > saved_high_score:
            with open('high_score.json', 'w') as f:
                json.dump(self.stats.high_score,f)
        
        sys.exit()
        
         
if __name__=='__main__':
    ai=AlienInvasion()
    ai.run_game()




