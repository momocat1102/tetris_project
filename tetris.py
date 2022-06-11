import random
import os
import time

import pygame as py

from blocks import COLOR_LIST_BORDER, COLOR_LIST_FILL, block_s, block_i, block_j, block_l, block_o, block_t, block_z

FPS = 60
WIDTH = 450
HIGHT = 601
BLOCK = 30
BLOCK_X_NUM = 10
BLOCK_Y_NUM = 20

BG_COLOR = (10, 10, 10)
BG_COLOR_RIGHT = (2, 222, 131)
BG_COLOR_RIGHT_LINE = (0, 117, 0)
TEXT_COLOR = (255, 255, 255)
RED = (255, 0, 0)

# 介面
Control_Interface = (30, HIGHT/2 - 120, WIDTH - 60, 240)

def Judge_Left_move(present_block, present_block_x, present_block_y, initial_map):
    # 判斷左移
    next_x = present_block_x - 1
    for y, line in enumerate(present_block):
        for x, block in enumerate(line):
            # 判斷左邊界
            if block != 0 and next_x + x < 0:
                return False
    # 判斷跟其他方塊有無碰撞
    if Judge_collision(present_block, next_x, present_block_y, initial_map):
        return True
    else:
        return False

def Judge_Right_move(present_block, present_block_x, present_block_y, initial_map):
    # 判斷右移
    next_x = present_block_x + 1
    for y, line in enumerate(present_block):
        for index in range(len(line) - 1, -1, -1):
            # 判斷右邊界
            if line[index] != 0 and next_x + index > BLOCK_X_NUM - 1:
                return False
    # 判斷跟其他方塊有無碰撞
    if Judge_collision(present_block, next_x, present_block_y, initial_map):
        return True
    else:
        return False

def Judge_Rotation_move(present_block, present_block_x, present_block_y, initial_map, rotate_sound):
    # 判斷旋轉(順轉)
    # 找出是哪一個形狀(抓出他的list)
    present_block_style_list = None
    for blocks in [block_i, block_j, block_l, block_o, block_s, block_t, block_z]:
        if present_block in blocks:
            present_block_style_list = blocks
    # 將其旋轉後，再來判斷
    for index in range(len(present_block_style_list)):
        if present_block == present_block_style_list[index]:
            next_index = index + 1
            if next_index >= len(present_block_style_list):
                next_index = next_index % len(present_block_style_list)
            next_block = present_block_style_list[next_index]
    # 判斷左右下邊界
    for y, line in enumerate(next_block):
        # 判斷左邊
        if present_block_x < 0:
            left_x = 0
            left_check = True
            while left_check and left_x < len(line):
                if line[left_x] != 0:         
                    while present_block_x + left_x < 0:
                        present_block_x += 1
                        left_check = False
                left_x += 1
        # 判斷右邊
        else:
            right_x = len(line) - 1
            right_check = True
            while right_check and right_x > 0:
                if line[right_x] != 0:
                    while present_block_x + right_x > BLOCK_X_NUM - 1:
                        present_block_x -= 1
                        right_check = False
                right_x -= 1
        # 判斷下面
        line_have_block = False
        for check in range(1, 8):
            if check in line:
                line_have_block = True
        if line_have_block:
            while present_block_y + y > BLOCK_Y_NUM - 1:
                present_block_y += 1
    # 判斷跟其他方塊有無碰撞
    if not Judge_collision(next_block, present_block_x, present_block_y, initial_map):
        if Judge_collision(next_block, present_block_x + 1, present_block_y, initial_map):
            present_block_x += 1
        elif Judge_collision(next_block, present_block_x - 1, present_block_y, initial_map):
            present_block_x -= 1
        elif Judge_collision(next_block, present_block_x, present_block_y - 1, initial_map):
            present_block_y -= 1
        else:
            return present_block_x, present_block_y, present_block
    present_block = next_block
    rotate_sound.play()
    return present_block_x, present_block_y, present_block

def Judge_Down_move(present_block, present_block_x, present_block_y, initial_map):
    # 判斷下落
    next_y = present_block_y + 1
    for y, line in enumerate(present_block):
        # 判斷是否到底了
        line_have_block = False
        for check in range(1, 8):
            if check in line:
                line_have_block = True
        if line_have_block and next_y + y > BLOCK_Y_NUM - 1:
            return False
    # 判斷跟其他方塊有無碰撞
    if Judge_collision(present_block, present_block_x, next_y, initial_map):
        return True
    else:
        return False

def Get_Mapblocks_position(initial_map):
    # 獲取map中有block的位置
    all_stop_blocks = []
    for y, line in enumerate(initial_map):
        for x, block in enumerate(line):
            if block != 0:
                all_stop_blocks.append((x, y))
    return all_stop_blocks

def Judge_collision(present_block, present_block_x, present_block_y, initial_map):
    # 判斷跟其他方塊的碰撞
    all_stop_blocks = Get_Mapblocks_position(initial_map)
    for y, line in enumerate(present_block):
        for x, block in enumerate(line):
            if block != 0 and (present_block_x + x, present_block_y + y) in all_stop_blocks:
                return False
    return True

def Add_Stop_Blocks(initial_map, present_block, present_block_x, present_block_y):
    # 將停止的方塊加入map
    for y, line in enumerate(present_block):
        for x, block in enumerate(line):
            if block != 0:
                initial_map[present_block_y + y][present_block_x + x] = block

def Judge_Game_over(initial_map, game_over_sound):
    # 判斷遊戲是否結束
    for line in [initial_map[0], initial_map[1]]:
        for block in range(3, 7):
            if line[block] != 0:
                game_over_sound.play()
                return True
    return False

def Random_Block():
    # 隨機方塊
    blocks_list = random.choice([block_i, block_j, block_l, block_o, block_s, block_t, block_z, block_j, block_l])
    return blocks_list[0]

def Check_Block_Not_Repeat(present_block, next_block):
    # 讓下一個block不重複
    while present_block == next_block:
        next_block = Random_Block()
    return present_block, next_block

def Run_Next_Block(next_block):
    next_block.pop(0)
    next_block.append(Random_Block())
    next_block[-2], next_block[-1] = Check_Block_Not_Repeat(next_block[-2], next_block[-1])

def Score_Count(row):
    # 處理分數
    if row == 0:
        return 0
    score_list = {1:100, 2:300, 3:500, 4:800}
    return score_list[row]

def Eliminate_Block(initial_map, collapse_sound):
    # 將方塊消去並下落
    move_line_num = list()
    # 消去滿格的行並下落
    for y, line in enumerate(initial_map):
        if 0 not in line:
            move_line_num.append(y)
            initial_map.pop(y)
            initial_map.insert(0, [0 for _ in range(len(line))])        
    # 沒有則回傳
    if not move_line_num:
        return 0
    # 回傳消了幾行
    collapse_sound.play()
    return len(move_line_num)

def Speed(eliminate_row):
    level_list = [('1', 0.5, 0, 10), ('2', 0.4, 11, 20),('3', 0.3, 21, 30),('4', 0.2, 31, 45), ('5', 0.1, 46, None)]
    for score_info, speed, start, end in level_list:
        if end and start <= eliminate_row <= end:
            return score_info, speed
        elif end is None and eliminate_row >= start:
            return score_info, speed

def Write_Next_Block(screen, next_block, next_block_x, next_block_y):
    # 畫出下一個要出現的block
    block_x = next_block_x
    block_y = next_block_y
    for index, now_block in enumerate(next_block):
        if index > 0:
            block_x = next_block_x
            block_y = next_block_y + ((index * 3) + 1 ) * BLOCK
        if now_block == block_i[0] or now_block == block_o[0]:
            block_x -= BLOCK/2
        for y, line in enumerate(now_block):
            for x, block in enumerate(line):
                if block != 0:
                    py.draw.rect(screen, COLOR_LIST_FILL[block], (block_x + (x * BLOCK), block_y + (y * BLOCK), BLOCK, BLOCK), 0, 4) # 方塊
                    py.draw.rect(screen, COLOR_LIST_BORDER[block], (block_x + (x * BLOCK) + 1, block_y + (y * BLOCK) + 1, BLOCK - 2, BLOCK - 2), 1, 4) # 框

def Write_Predict_Blocks(screen, initial_map, present_block, present_block_x, present_block_y):
    # 畫出預測方塊
    while Judge_Down_move(present_block, present_block_x, present_block_y, initial_map):
        present_block_y += 1
    for y, line in enumerate(present_block):
            for x, block in enumerate(line):
                if block != 0:
                    py.draw.rect(screen, COLOR_LIST_BORDER[block], ((present_block_x + x) * BLOCK + 1, (present_block_y + y) * BLOCK + 1, BLOCK - 2, BLOCK - 2), 1, 4)

def Write_Control_Interface(screen, text_start, text_start_rect):
    # 畫出介面
    py.draw.rect(screen, BG_COLOR_RIGHT, Control_Interface, 0, 5)
    py.draw.rect(screen, BG_COLOR_RIGHT_LINE, Control_Interface, 3, 5)
    # 畫開始鍵
    py.draw.rect(screen, BG_COLOR_RIGHT_LINE, text_start_rect, 0, 4)
    py.draw.rect(screen, BG_COLOR, text_start_rect, 2, 4)
    screen.blit(text_start, text_start_rect)

def Write_Rule(screen):
    # 畫出規則
    py.draw.rect(screen, BG_COLOR, (50, HIGHT/2 - 100, WIDTH - 100, 160), 0, 5)
    font = py.font.Font('font.ttf', 24)
    rule_1 = font.render("← → 控制左右  空白鍵快速掉落", True, TEXT_COLOR)
    rule_2 = font.render("↓下降一格  p暫停鍵  五個level", True, TEXT_COLOR)
    rule_3 = font.render("每消掉10行升一個level", True, TEXT_COLOR)
    rule_4 = font.render("分數計算為：   1行:100 2行:300", True, TEXT_COLOR)
    rule_5 = font.render("3行:500 4行:800", True, TEXT_COLOR)
    screen.blit(rule_1, (55, HIGHT/2 - 100))
    screen.blit(rule_2, (56, HIGHT/2 - 70))
    screen.blit(rule_3, (100, HIGHT/2 - 40))
    screen.blit(rule_4, (53, HIGHT/2 - 10))
    screen.blit(rule_5, (215, HIGHT/2 + 20))

def Write_End(screen, score):
    # 畫出結算分數
    py.draw.rect(screen, BG_COLOR, (50, HIGHT/2 - 100, WIDTH - 100, 160), 0, 5)
    font = py.font.Font('font.ttf', 50)
    font1 = py.font.Font('font.ttf', 25)
    game_end = font.render("GAME OVER", True, RED)
    Score = font1.render("您的得分為：   " + str(score), True, TEXT_COLOR)
    screen.blit(game_end, (75, HIGHT/2 - 100))
    screen.blit(Score, (90, HIGHT/2 - 10))
    
def Write_Stop(screen):
    # 畫出暫停介面
    py.draw.rect(screen, BG_COLOR, (50, HIGHT/2 - 100, WIDTH - 100, 160), 0, 5)
    font = py.font.Font('font.ttf', 100)
    stop = font.render("暫停", True, RED)
    screen.blit(stop, (125, HIGHT/2 - 90))

def main():
    py.init()
    py.mixer.init()
    screen = py.display.set_mode((WIDTH, HIGHT))
    py.display.set_caption("Tetris")
    clock = py.time.Clock()
    # 初始化
    initial_map = [[0 for i in range(BLOCK_X_NUM)] for j in range(BLOCK_Y_NUM)]
    present_block = Random_Block()
    # 製造三個next_block
    next_block = list()
    for next in range(3):
        # 確認不重複
        if next != 0:
            next_block.append(Random_Block())
            next_block[next - 1], next_block[next] = Check_Block_Not_Repeat(next_block[next - 1], next_block[next])
        else:
            next_block.append(Random_Block())
            present_block, next_block[next] = Check_Block_Not_Repeat(present_block, next_block[next])

    present_block_x = 3
    present_block_y = 0
    spead_down = False
    last_time = time.time()
    speed = 0.5
    speed_info = '1'
    
    # Text
    font = py.font.Font('font.ttf', 24)
    text_start = font.render("START", True, TEXT_COLOR)
    text_start_rect = text_start.get_rect(center =(WIDTH/2, HIGHT/2 + 90))
    # 音效
    move_sound = py.mixer.Sound(os.path.join("sound", "move.wav"))
    spead_sound = py.mixer.Sound(os.path.join("sound", "hardDrop.wav"))
    rotate_sound = py.mixer.Sound(os.path.join("sound", "rotate.wav"))
    collapse_sound = py.mixer.Sound(os.path.join("sound", "collapse.wav"))
    hold_sound = py.mixer.Sound(os.path.join("sound", "hold.wav"))
    levelup_sound = py.mixer.Sound(os.path.join("sound", "levelUp.wav"))
    game_over_sound = py.mixer.Sound(os.path.join("sound", "game_over.wav"))

    py.mixer.music.load(os.path.join("sound", "background.wav"))

    # 分數
    score = 0
    # 消除的行數
    eliminate_row = 0

    # 判斷遊戲是否結束
    game_over = False
    again_button = False

    # 暫停
    stop = False
     
    #遊戲開始
    game_start = False
    py.mixer.music.play(-1)
    # 遊戲迴圈
    running = True
    while running:
        for event in py.event.get():
            if event.type == py.QUIT:
                running = False
            elif event.type == py.KEYDOWN:
                # 按鍵控制
                if event.key == py.K_LEFT:
                    if Judge_Left_move(present_block, present_block_x, present_block_y, initial_map) and game_start and not stop:
                        present_block_x -= 1
                        move_sound.play()
                elif event.key == py.K_RIGHT:
                    if Judge_Right_move(present_block, present_block_x, present_block_y, initial_map) and game_start and not stop:
                        present_block_x += 1
                        move_sound.play()
                elif event.key == py.K_UP:
                    if game_start and not stop:
                        present_block_x, present_block_y, present_block = Judge_Rotation_move(present_block, present_block_x, present_block_y, initial_map, rotate_sound)
                elif event.key == py.K_DOWN:
                    if Judge_Down_move(present_block, present_block_x, present_block_y, initial_map) and game_start and not stop:
                        present_block_y += 1
                        move_sound.play()
                elif event.key == py.K_SPACE and game_start and not stop:
                    spead_down = True
                elif event.key == py.K_p:
                    stop = True
            elif event.type == py.MOUSEBUTTONDOWN:
                if text_start_rect.collidepoint(event.pos):
                    move_sound.play()
                    if not game_start:
                        game_start = True
                    elif stop:
                        stop = False
                    elif not again_button:
                        again_button = True
        if not game_over and spead_down:
            while Judge_Down_move(present_block, present_block_x, present_block_y, initial_map):
                present_block_y += 1
            # 將已停止的方塊加入map
            Add_Stop_Blocks(initial_map, present_block, present_block_x, present_block_y)
            # 消除方塊
            row = Eliminate_Block(initial_map, collapse_sound)
            # 加分
            score += Score_Count(row)
            # 檢查速度
            eliminate_row += row
            old_info = speed_info
            speed_info, speed = Speed(eliminate_row)
            if old_info != speed_info:
                levelup_sound.play()
            # 換新的圖形
            present_block = next_block[0]
            Run_Next_Block(next_block)
            # 判斷遊戲是否結束
            game_over = Judge_Game_over(initial_map, game_over_sound)
            # 重製座標
            present_block_x = 3
            present_block_y = 0
            spead_down = False
            # 音效
            spead_sound.play()
        else:
            if game_start and not game_over and not stop and time.time() - last_time > speed:
                last_time = time.time()
                if Judge_Down_move(present_block, present_block_x, present_block_y, initial_map):
                    present_block_y += 1
                else:
                    # 將已停止的方塊加入map
                    Add_Stop_Blocks(initial_map, present_block, present_block_x, present_block_y)
                    # 消除方塊
                    row = Eliminate_Block(initial_map, collapse_sound)
                    # 加分
                    score += Score_Count(row)
                    # 檢查速度
                    eliminate_row += row
                    old_info = speed_info
                    speed_info, speed = Speed(eliminate_row)
                    if old_info != speed_info:
                        levelup_sound.play()
                    # 換新的圖形
                    present_block = next_block[0]
                    Run_Next_Block(next_block)
                    # 判斷遊戲是否結束
                    game_over = Judge_Game_over(initial_map, game_over_sound)
                    # 重製座標
                    present_block_x = 3
                    present_block_y = 0
                    spead_down = False
                    hold_sound.play()
        
        # 顯示背景
        screen.fill(BG_COLOR)

        # 顯示輸的格子
        for y in range(2):
            for x in range(3, 7):
                py.draw.rect(screen, (77, 0, 0), (x * BLOCK, y * BLOCK, BLOCK, BLOCK), 0)

        # 畫網格線 X
        for y in range(BLOCK_Y_NUM + 1):
            py.draw.line(screen, (128, 128, 128), (0, y * BLOCK), (BLOCK_X_NUM * BLOCK, y * BLOCK), 1)

        # 畫網格線 Y    
        for x in range(BLOCK_X_NUM + 1):
            py.draw.line(screen, (128, 128, 128), (x * BLOCK, 0), (x * BLOCK, BLOCK_Y_NUM * BLOCK), 1)
        
        # 顯示目前圖形
        for y, line in enumerate(present_block):
            for x, block in enumerate(line):
                if block != 0:
                    py.draw.rect(screen, COLOR_LIST_FILL[block], ((present_block_x + x) * BLOCK, (present_block_y + y) * BLOCK, BLOCK, BLOCK), 0, 4) # 方塊
                    py.draw.rect(screen, COLOR_LIST_BORDER[block], ((present_block_x + x) * BLOCK + 1, (present_block_y + y) * BLOCK + 1, BLOCK - 2, BLOCK - 2), 1, 4) # 框
        
        #顯示預測值
        Write_Predict_Blocks(screen, initial_map, present_block, present_block_x, present_block_y)
        
        # 顯示之前的圖形
        for y, line in enumerate(initial_map):
            for x, block in enumerate(line):
                if block != 0:
                    py.draw.rect(screen, COLOR_LIST_FILL[block], (x * BLOCK, y * BLOCK, BLOCK, BLOCK), 0, 4) # 方塊
                    py.draw.rect(screen, COLOR_LIST_BORDER[block], (x * BLOCK + 1, y * BLOCK + 1, BLOCK - 2, BLOCK - 2), 1, 4) # 框
        
        # 顯示面板
        py.draw.rect(screen, BG_COLOR_RIGHT, (BLOCK_X_NUM * BLOCK + 2, 0, WIDTH - (BLOCK_X_NUM * BLOCK + 2), HIGHT), 0)
        # 下一個方塊
        py.draw.rect(screen, BG_COLOR, (BLOCK_X_NUM * BLOCK + 4, 2, WIDTH - (BLOCK_X_NUM * BLOCK + 6), HIGHT/2 - 2), 0, 4)
        Write_Next_Block(screen, next_block, BLOCK_X_NUM * BLOCK + 30 , 10)
        
        # 分數
        py.draw.rect(screen, BG_COLOR, (BLOCK_X_NUM * BLOCK + 4, HIGHT/2 + 60, WIDTH - (BLOCK_X_NUM * BLOCK + 6), 235), 0, 4)
        score_show_msg = font.render('得分：', True, (255, 255, 255))
        screen.blit(score_show_msg, (BLOCK_X_NUM * BLOCK + 10, HIGHT/2 + 65))
        score_show_msg = font.render(str(score), True, (255, 255, 255))
        screen.blit(score_show_msg, (BLOCK_X_NUM * BLOCK + 10, HIGHT/2 + 105))

        # 速度
        score_show_msg = font.render('Level：', True, (255, 255, 255))
        screen.blit(score_show_msg, (BLOCK_X_NUM * BLOCK + 10, HIGHT/2 + 145))
        score_show_msg = font.render(speed_info, True, (255, 255, 255))
        screen.blit(score_show_msg, (BLOCK_X_NUM * BLOCK + 10, HIGHT/2 + 185))

        if not game_start:
            Write_Control_Interface(screen, text_start, text_start_rect)
            Write_Rule(screen)
        if stop and game_start:
            Write_Control_Interface(screen, text_start, text_start_rect)
            Write_Stop(screen)
        if game_over:
            Write_Control_Interface(screen, text_start, text_start_rect)
            Write_End(screen, score)
            if again_button:
                # 全部初始化
                initial_map = [[0 for i in range(BLOCK_X_NUM)] for j in range(BLOCK_Y_NUM)]
                present_block = Random_Block()
                # 製造三個next_block
                next_block = list()
                for next in range(3):
                    # 確認不重複
                    if next != 0:
                        next_block.append(Random_Block())
                        next_block[next - 1], next_block[next] = Check_Block_Not_Repeat(next_block[next - 1], next_block[next])
                    else:
                        next_block.append(Random_Block())
                        present_block, next_block[next] = Check_Block_Not_Repeat(present_block, next_block[next])
                present_block_x = 3
                present_block_y = 0
                spead_down = False
                last_time = time.time()
                speed = 0.5
                speed_info = '1'
                # 分數
                score = 0
                # 消除的行數
                eliminate_row = 0
                game_over = False
                again_button = False


        py.display.update()
        clock.tick(FPS)


if __name__ == '__main__':
    main()