import pygame
import sys
import os
import math
import random

# ====================================================
#  1. 初期設定・定数 (SETTINGS)
# ====================================================

# 実行環境のディレクトリに移動 (資料の条件)
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 画面設定
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TILE_SIZE = 40

# 色定義
WHITE  = (255, 255, 255)
BLACK  = (0, 0, 0)
RED    = (255, 50, 50)     # 通常こうかとん
BLUE   = (50, 50, 255)     # タワー
YELLOW = (255, 255, 0)     # 弾
PURPLE = (180, 0, 255)     #エリートカラー

# トラップの色定義
trap_color = (255, 165, 0)  # トラップの色
# ORANGE = (255, 165, 0)
# PURPLE = ...

# マップチップ
TILE_PATH = 0
TILE_GRASS = 1
TILE_BASE = 2
TILE_SPAWN = 3

# ゲーム状態
STATE_PLAY = 1

STATE_GAMEOVER = 2

# ====================================================
#  2. クラス定義エリア
# ====================================================

class GameManager:
    def __init__(self):
        self.chicken = 100
        self.life = 10
        self.state = STATE_PLAY
        self.fever_gauge = 0 
        self.is_fever = False
        self.fever_timer = 0
        self.FEVER_DURATION = FPS * 20

    def activate_fever(self):
        if not self.is_fever:
            self.fever_timer = self.FEVER_DURATION
            self.is_fever = True
            self.fever_gauge = 0 
            print("--- FEVER TIME START! ---")

    def update(self):
        if self.is_fever:
            self.fever_timer -= 1
            if self.fever_timer <= 0:
                self.is_fever = False
                print("--- FEVER TIME END! ---")

    # --- ここを変更・追加 ---
    def check_gameover(self):
        """ライフが0以下になったら状態をゲームオーバーにする"""
        if self.life <= 0:
            self.state = STATE_GAMEOVER

    def reset_game(self):
        """ゲーム変数を初期値に戻す"""
        self.chicken = 100
        self.life = 10
        self.state = STATE_PLAY
        self.fever_gauge = 0
        self.is_fever = False
        self.fever_timer = 0
    # -----------------------


class MapManager:
    def __init__(self):
        # 0:道, 1:草, 2:拠点, 3:出現
        # 縦15行 x 横20列 (600px x 800px)
        self.map_data = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1],
            [1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1],
            [1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1],
            [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        ]
        
        # 敵が通るルートの座標 (マスの中心座標: index * 40 + 20)
        # 上記のmap_dataの「曲がり角」に合わせて正確に設定
        self.waypoints = [
            (60, 100),    # [1][2] スタート
            (500, 100),   # [12][2] 右へ（最初の角）
            (500, 260),  # [12][6] 下へ（次の角）
            (220, 260),  # [5][6] 左へ
            (220, 500),  # [5][12] 下へ
            (660, 500),  # [16][12] 右へ
            (660, 380)   # [16][9] 右へ（ゴール）
        ]

        # 【追加箇所】スポーン・拠点画像の読み込み (元のプログラムの115行目以降に追加)
        try:
            self.base_img = pygame.image.load(os.path.join("fig", "KL.jpg")).convert_alpha()
            self.base_img = pygame.transform.scale(self.base_img, (TILE_SIZE, TILE_SIZE))
        except:
            self.base_img = None

        try:
            self.goal_img = pygame.image.load(os.path.join("fig", "TU.jpg")).convert_alpha()
            self.goal_img = pygame.transform.scale(self.goal_img, (TILE_SIZE, TILE_SIZE))
        except:
            self.goal_img = None

    def draw(self, screen, is_fever=False):
        # 【担当E】is_feverフラグを受け取り、フィーバー中は背景色を変えてください
        if is_fever:
            grass_color = (255, 215, 0)  # フィーバー中の背景色（金色）
        else:
            grass_color = (0, 100, 0)
        screen.fill(BLACK) 
    
        for r, row in enumerate(self.map_data):
            for c, tile in enumerate(row):
                rect = pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if tile == TILE_PATH: color = (240, 230, 140)
                elif tile == TILE_GRASS: color = grass_color
                elif tile == TILE_BASE: color = BLUE
                elif tile == TILE_SPAWN: color = RED
                else: color = BLACK
                
                pygame.draw.rect(screen, color, rect)
                
                # 【追加箇所】スポーンと拠点に画像を表示 (元のプログラム130行目付近)
                if (tile == TILE_SPAWN) and self.base_img:
                    screen.blit(self.base_img, rect)
                if (tile == TILE_BASE) and self.goal_img:
                    screen.blit(self.goal_img, rect)

                pygame.draw.rect(screen, (0, 50, 0), rect, 1)
    
    def is_placeable(self, x, y):
        c = x // TILE_SIZE
        r = y // TILE_SIZE
        if 0 <= r < len(self.map_data) and 0 <= c < len(self.map_data[0]):
            return self.map_data[r][c] == TILE_GRASS
        return False
    

    # トラップ設置判定
    def is_path(self, x, y):
        c = x // TILE_SIZE
        r = y // TILE_SIZE
        if 0 <= r < len(self.map_data) and 0 <= c < len(self.map_data[0]):
            return self.map_data[r][c] == TILE_PATH
        return False


class Koukaton(pygame.sprite.Sprite):
    """
    敵キャラクタークラス
    """
    def __init__(self, waypoints, is_elite = False):
        super().__init__()
        # 【修正箇所】Surface作成を画像読み込みに変更 (元のプログラム144行目)
        try:
            self.image = pygame.image.load(os.path.join("fig", "enemy.png")).convert_alpha()
            size = (35, 35) if is_elite else (25, 25)
            self.image = pygame.transform.scale(self.image, size)
            if is_elite:
                self.image.fill(PURPLE, special_flags=pygame.BLEND_RGB_MULT)
        except:
            self.image = pygame.Surface((20, 20))
            self.image.fill(PURPLE if is_elite else RED) # エリートなら色を変える

        self.rect = self.image.get_rect()
        
        self.waypoints = waypoints
        self.wp_index = 0
        self.speed = 3 if is_elite else 2   # エリートなら速くする
        self.hp = 60 if is_elite else 30     # エリートなら体力を増やす
        self.value = 30 if is_elite else 10  # エリートなら撃破報酬を増やす

        if waypoints:
            self.rect.center = waypoints[0]

    def update(self, gm):
        if self.wp_index < len(self.waypoints) - 1:
            target = self.waypoints[self.wp_index + 1]
            dx = target[0] - self.rect.centerx
            dy = target[1] - self.rect.centery
            
            if dx > 0: self.rect.centerx += min(self.speed, dx)
            elif dx < 0: self.rect.centerx -= min(self.speed, -dx)
            if dy > 0: self.rect.centery += min(self.speed, dy)
            elif dy < 0: self.rect.centery -= min(self.speed, -dy)
            
            if abs(dx) < 5 and abs(dy) < 5:
                self.wp_index += 1
        else:
            gm.life -= 1
            self.kill()



# 敵と衝突したらダメージを与える処理
class Trap(pygame.sprite.Sprite):
    """
    トラップクラス（道に設置し、敵にダメージを与える）
    """
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        # トラップを分かりやすくするため、半透明のTRAP_COLORにする
        self.image.fill(trap_color) # 変数をTRAP_COLORに修正
        self.image.set_alpha(150) # 半透明化
        self.rect = self.image.get_rect(topleft=(x, y))

        self.damage = 20 # 衝突時のダメージ量
        self.life = 1   # トラップの耐久回数（1回衝突したら消える）

    def update(self, enemy_group, gm):
         # 敵との衝突判定をメインループではなく、トラップのupdate内で行う
        hits = pygame.sprite.spritecollide(self, enemy_group, False)

        if hits:
            for enemy in hits:
                enemy.hp -= self.damage
                self.life -= 1
                print(f"Trap hit! Enemy HP: {enemy.hp}, Trap Life: {self.life}")
                    
                # --- 追加：敵の死亡判定 ---
                if enemy.hp <= 0:
                    gm.chicken += enemy.value  # 報酬を加算
                    enemy.kill()               # 敵を消滅させる

        # トラップの耐久が0になったら削除
        if self.life <= 0:
            self.kill()

class Tower(pygame.sprite.Sprite):
    """
    タワークラス
    """
    def __init__(self, x, y):
        super().__init__()
        # 【修正箇所】Surface作成を画像読み込みに変更 (元のプログラム214行目)
        try:
            self.image = pygame.image.load(os.path.join("fig", "tower.png")).convert_alpha()
            self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        except:
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.image.fill(BLUE)

        self.rect = self.image.get_rect(topleft=(x, y))
        
        self.range = 150
        self.cooldown = 30
        self.timer = 0
        
        self.level = 1 # 現在のレベル
        self.max_level = 5 #　最大レベル
        self.cost = 50 #基本強化コスト
        
    def get_upgrade_cost(self):
        """
        タワーの強化コストを計算するメソッド
        """
        return self.cost * self.level
    
    def upgrade(self):
        """
        タワーの強化メソッド
        """
        if self.level < self.max_level:
            self.level += 1
            self.range += 20
            self.cooldown = max(5, self.cooldown - 5)
            
            # 強化の視覚効果（画像の場合は少し色を重ねる等）
            self.image.fill((20, 20, 20), special_flags=pygame.BLEND_RGB_ADD)
            
    def update(self, enemy_group, bullet_group, is_fever=False):
        # 【担当E】is_feverフラグを受け取り、フィーバー中はクールダウンを短くしてください
        # 通常のクールダウン時間
        current_cooldown = self.cooldown
        # フィーバー中はクールダウンを短縮 (例: 半分にする)
        if is_fever:
            current_cooldown = self.cooldown // 2          
        self.timer += 1
        if self.timer >= current_cooldown:
            nearest_enemy = None
            min_dist = self.range
            for enemy in enemy_group:
                dist = math.hypot(self.rect.centerx - enemy.rect.centerx,
                                  self.rect.centery - enemy.rect.centery)
                if dist <= min_dist:
                    min_dist = dist
                    nearest_enemy = enemy
            
            if nearest_enemy:
                new_bullet = Bullet(self.rect.center, nearest_enemy.rect.center)
                bullet_group.add(new_bullet)
                self.timer = 0


class Bullet(pygame.sprite.Sprite):
    """
    弾クラス
    """
    def __init__(self, start_pos, target_pos):
        super().__init__()
        # 【修正箇所】Surface作成を画像読み込みに変更 (元のプログラム260行目)
        try:
            self.image = pygame.image.load(os.path.join("fig", "chicken.png")).convert_alpha()
            self.image = pygame.transform.scale(self.image, (20, 20))
        except:
            self.image = pygame.Surface((8, 8))
            self.image.fill(YELLOW)

        self.rect = self.image.get_rect(center=start_pos)
        self.speed = 10
        
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        distance = math.hypot(dx, dy)
        if distance == 0: distance = 1
        
        self.vx = (dx / distance) * self.speed
        self.vy = (dy / distance) * self.speed
        self.life_timer = 60

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        self.life_timer -= 1
        if self.life_timer <= 0:
            self.kill()


# ====================================================
#  3. メインループ
# ====================================================

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Koukaton Defense Base")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 40)
    large_font = pygame.font.SysFont(None, 80) # サイズを少し大きく修正

    gm = GameManager()
    map_manager = MapManager()
    
    enemy_group = pygame.sprite.Group()
    tower_group = pygame.sprite.Group()
    bullet_group = pygame.sprite.Group()
    
    trap_group = pygame.sprite.Group()
    # 初期配置（テスト用）
    tower_group.add(Tower(14 * TILE_SIZE, 4 * TILE_SIZE))
    
    spawn_timer = 0
    TRAP_COST = 20  # トラップの設置コスト
    
    start_ticks = pygame.time.get_ticks()
    
    running = True
    while running:
        # --- 1. イベント処理 ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                
                # 左クリック：タワー配置
                if event.button == 1:
                    clicked_towers = [t for t in tower_group if t.rect.collidepoint(mx, my)]
                    if clicked_towers:
                        target_tower = clicked_towers[0]
                        cost = target_tower.get_upgrade_cost()
                        
                        if target_tower.level < target_tower.max_level and gm.chicken >= cost:
                            gm.chicken -= cost
                            target_tower.upgrade()
                    
                    # 新規配置
                    elif map_manager.is_placeable(mx, my):
                         cost = 100
                         if gm.chicken >= cost:
                             gm.chicken -= cost
                             tower_group.add(Tower((mx//TILE_SIZE)*TILE_SIZE, (my//TILE_SIZE)*TILE_SIZE))

                # 右クリック：トラップ配置
                if event.button == 3: # 右クリック 
                    tx = (mx // TILE_SIZE) * TILE_SIZE
                    ty = (my // TILE_SIZE) * TILE_SIZE
        
                    if map_manager.is_path(mx, my) and gm.chicken >= TRAP_COST:
                        existing_trap = None
                        for trap in trap_group:
                            if trap.rect.topleft == (tx, ty):
                                existing_trap = trap
                                break
        
                        if not existing_trap:
                            gm.chicken -= TRAP_COST
                            trap_group.add(Trap(tx, ty))
                            print(f"Trap placed at ({tx}, {ty}). Cost: {TRAP_COST}")
                
            # 【担当E】フィーバー発動キー（Fキー）
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    if gm.fever_gauge >= 30:
                        gm.activate_fever()
       
                if event.key == pygame.K_r:
                    start_ticks = pygame.time.get_ticks()
                    gm.reset_game()
                    enemy_group.empty()                        
                    bullet_group.empty()
                    tower_group.empty()
                    trap_group.empty()
                    tower_group.add(Tower(14 * TILE_SIZE, 4 * TILE_SIZE))
                    spawn_timer = 0
                elif event.key == pygame.K_q:
                    running = False


        # --- 2. 更新処理 ---

        if gm.state == STATE_PLAY:
            gm.update()
            
            elapsed_time = (pygame.time.get_ticks() - start_ticks) / 1000
            difficulty_scale = elapsed_time / 30
            
            spawn_interval = 50 if gm.is_fever else 120
            spawn_timer += 1
            
            if spawn_timer >= spawn_interval: 
                spawn_timer = 0
                is_elite = random.random() < 0.2
                new_enemy = Koukaton(map_manager.waypoints, is_elite)
                
                new_enemy.hp += int(30 * difficulty_scale)
                new_enemy.speed += (0.6 * difficulty_scale)
                enemy_group.add(new_enemy)
            
            enemy_group.update(gm)
            tower_group.update(enemy_group, bullet_group, gm.is_fever) 
            bullet_group.update()
            trap_group.update(enemy_group, gm)

            hits = pygame.sprite.groupcollide(bullet_group, enemy_group, True, False)
            for bullet, hit_enemies in hits.items():
                for enemy in hit_enemies:
                    enemy.hp -= 10
                    if enemy.hp <= 0:
                        enemy.kill()
                        gm.chicken += enemy.value
                        if not gm.is_fever:
                            gm.fever_gauge = min(30, gm.fever_gauge + 1)

            gm.check_gameover()

        # --- 3. 描画処理 ---
        screen.fill(BLACK)
        
        if gm.state == STATE_PLAY:
            map_manager.draw(screen, gm.is_fever)
            tower_group.draw(screen)
            enemy_group.draw(screen)
            bullet_group.draw(screen)
            trap_group.draw(screen)
            
            txt_chicken = font.render(f"Chicken: {gm.chicken}", True, WHITE)
            txt_life = font.render(f"Life: {gm.life}", True, WHITE)
            screen.blit(txt_chicken, (10, 10))
            screen.blit(txt_life, (10, 50))
            
            FEVER_MAX = 30
            gauge_ratio = gm.fever_gauge / FEVER_MAX
            pygame.draw.rect(screen, (50, 50, 50), (10, 550, 150, 20), 0)
            pygame.draw.rect(screen, (255, 0, 255), (10, 550, 150 * gauge_ratio, 20), 0)
            txt_fever = font.render(f"Fever: {gm.fever_gauge}/{FEVER_MAX}", True, WHITE)
            screen.blit(txt_fever, (170, 550))

            if gm.is_fever:
                sec = gm.fever_timer // FPS + 1
                txt_fever_time = font.render(f"FEVER TIME! ({sec}s)", True, (255, 0, 255))
                screen.blit(txt_fever_time, (SCREEN_WIDTH // 2 - txt_fever_time.get_width() // 2, 10))

        elif gm.state == STATE_GAMEOVER:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            screen.blit(overlay, (0,0))
            
            txt_over = large_font.render("GAME OVER", True, RED)
            txt_retry = font.render("Press R to Restart / Q to Quit", True, WHITE)
            
            screen.blit(txt_over, (SCREEN_WIDTH//2 - txt_over.get_width()//2, SCREEN_HEIGHT//2 - 50))
            screen.blit(txt_retry, (SCREEN_WIDTH//2 - txt_retry.get_width()//2, SCREEN_HEIGHT//2 + 50))
            
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()