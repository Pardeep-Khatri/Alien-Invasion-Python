#importing modules
import sys
from time import sleep
import pygame
from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien

#creating main class
class AlienInvasion:
    def __init__(self):                  #create game resources
        pygame.init()                  #initialize background settings
        self.settings = Settings()
        self.screen = pygame.display.set_mode((0 , 0) , pygame.FULLSCREEN)      #fullsize screen
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption("Alien Invasion by Pardeep & Sumit")
      # Create an instance to store game statistics and Scoreboard
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group() #grouping

        self._create_fleet()

       # Make the Play button.
        self.play_button = Button(self, "Play")


    def run_game(self):
      while True:                     #Start the main loop for the game.
          self._check_events()
                #helper method
          if self.stats.game_active:
              self.ship.update()
              self._update_bullets()
              self._update_aliens()

          self._update_screen()        #helper method

    def _check_events(self):
        for event in pygame.event.get(): # Watch for keyboard and mouse events.
           if event.type == pygame.QUIT:
               sys.exit()
           elif event.type == pygame.KEYDOWN:
               self._check_keydown_events(event)
           elif event.type == pygame.KEYUP:
               self._check_keyup_events(event)
           elif event.type == pygame.MOUSEBUTTONDOWN:
               mouse_pos = pygame.mouse.get_pos()
               self._check_play_button(mouse_pos)

    def _check_play_button(self , mouse_pos):#star a game when player click player
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
             self.settings.initialize_dynamic_settings() #reset game settings
             self.stats.reset_stats() # Reset the game statistics.
             self.stats.game_active = True
             self.sb.prep_score()
             self.sb.prep_level()
             self.sb.prep_ships()
    #get rig of remaining aliens and bullets
             self.aliens.empty()
             self.bullets.empty()
  #creating new fleet ans ship(ship in center)
             self._create_fleet()
             self.ship.center_ship()
              # Hide the mouse cursor.
             pygame.mouse.set_visible(False)


    def _check_keydown_events(self, event):
#Respond to keypresses.
        if event.key == pygame.K_RIGHT:
           self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
           self.ship.moving_left = True
        elif event.key == pygame.K_q:
           sys.exit()
        elif event.key == pygame.K_SPACE:
           self._fire_bullet()



    def _check_keyup_events(self, event):
#Respond to key releases.
       if event.key == pygame.K_RIGHT:
          self.ship.moving_right = False
       elif event.key == pygame.K_LEFT:
          self.ship.moving_left = False
       elif event.key == pygame.K_q:
          sys.exit()

    def _fire_bullet(self):               #Create a new bullet and add it to the bullets group.
        if len(self.bullets) < self.settings.bullets_allowed:
              new_bullet = Bullet(self)
              self.bullets.add(new_bullet)

    def _update_bullets(self):        # Update bullet positions and get rid of old bullets
        self.bullets.update()
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        self._check_bullet_alien_collision()


    def _check_bullet_alien_collision(self):
        # Check for any bullets that have hit aliens.
        # If so, get rid of the bullet and the alien.
        collision = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
        if collision:
            for aliens in collision.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()

        if not self.aliens:# Destroy existing bullets and create new fleet.
           self.bullets.empty()
           self._create_fleet()
           self.settings.increase_speed()

          # Increase level.
           self.stats.level += 1
           self.sb.prep_level()


    def _update_aliens(self):  # check if fleet is at an edge ,Update the positions of all aliens in the fleet
        self._check_fleet_edges()
        self.aliens.update()
        # Look for alien-ship collisions.
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()
        # Look for aliens hitting the bottom of the screen.
        self._check_aliens_bottom()



    def _create_fleet(self):#make aliens
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)

        #Determine the number of rows of aliens that fit on the screen.
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height -(3 * alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_height)
# Create the first row of aliens.
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number,row_number)




    def _create_alien(self,alien_number, row_number):#Create an alien and place it in the row.
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)

    def _check_fleet_edges(self):
       for alien in self.aliens.sprites():
           if alien.check_edges():
               self._change_fleet_direction()
               break


    def _change_fleet_direction(self):#"""Drop the entire fleet and change the fleet's direction."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _ship_hit(self):
#Respond to the ship being hit by an alien.
      if self.stats.ships_left > 0:
       # Decrement ships_left.
         self.stats.ships_left -= 1
         self.sb.prep_ships()

# Get rid of any remaining aliens and bullets.
         self.aliens.empty()
         self.bullets.empty()
# Create a new fleet and center the ship.
         self._create_fleet()
         self.ship.center_ship()
# Pause.
         sleep(1)
      else:
        self.stats.game_active = False
        pygame.mouse.set_visible(True)


    def _check_aliens_bottom(self):#Check if any aliens have reached the bottom of the screen."""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
             if alien.rect.bottom >= screen_rect.bottom:
# Treat this the same as if the ship got hit.
               self._ship_hit()
               break



    def _update_screen(self):
        self.screen.fill(self.settings.bg_color)  # Redraw the screen during each pass through the loop.
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)
        # Draw the score information.
        self.sb.show_score()
        # Draw the play button if the game is inactive.
        if not self.stats.game_active:
            self.play_button.draw_button()
        pygame.display.flip()   # Make the most recently drawn screen visible.



if __name__ == '__main__':
    # Make a game instance, and run the game.
    ai_game = AlienInvasion()
    ai_game.run_game()
