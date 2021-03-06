from pybw_swig import * # import all constants and classes
import pybw
import math

from KaisevenOptimizeSC import *
from KaisevenControlSC import *
from StarCraftAIDevelopTool import *
from StarCraftAIBasicTool import *

class Sample(object):
    def __init__(self):
        # Add ourselves to the console manager as variable "k"
        pybw.consoleManager.locals.update({'k': self})

    def onConnect(self):
        # Get the game instance
        self.game = getGame() 

    def onMatchStart(self):
        if self.game.isReplay:
            return
        set_basic_information(self, self.game)
        initial_units_scan(self.me, scan_visible_enemy = True, game = self.game)

    def onSendText(self, message):
        self.message = message

    def onMatchFrame(self):
        frame_count = self.game.frameCount
        #self.game.printf(str(frame_count))
        self.su = list(self.game.selectedUnits)

        #if len(self.su) > 0:
        #    self.tsu = self.su[0]
        #    if self.tsu.isUnderAttack:
        #        draw_circle_on(self.game, self.tsu, radius = 14, color = COLOR_RED)
        #    if self.tsu.isIdle:
        #        draw_circle_on(self.game, self.tsu, radius = 10, color = COLOR_GREEN)
        #    elif self.tsu.isMoving:
        #        draw_circle_on(self.game, self.tsu, radius = 10, color = COLOR_BLUE)

        my_army = []
        for key in self.me.units_dictionary.keys():
            if key in self.me.unittype_set_army:
                my_army += list(self.me.units_dictionary[key])
        self.my_army = my_army
        my_enemy = list(self.me.visible_enemy_units)

        if len(my_army) > 0:
            for u in my_army:
                draw_circle_on(self.game, u, radius = u.type.groundWeapon.maxRange, color = COLOR_RED)
                draw_range_circle_on(self.game, u, move_coef = 1)
                #draw_circle_on(self.game, u, radius = int(fire_range_of(u)), color = COLOR_YELLOW)
            #self.game.drawCircleMap(x, y, 5, COLOR_CYAN)
            #self.game.drawCircleMap(x, y, 6, COLOR_CYAN)

    def onUnitDestroy(self, unit):
        #self.game.printf('Unit destroy : ' + unit.type.name)
        if unit.player == self.me:
            self.me.units_dictionary[unit.type].remove(unit)

    def onUnitCreate(self, unit):
        pass

    def onUnitMorph(self, unit):
        pass

    def onUnitComplete(self, unit):
        #self.game.printf('Unit complete : ' + unit.type.name)
        if unit.player == self.me:
            self.me.units_dictionary[unit.type].add(unit)

    def onUnitHide(self, unit):
        #self.game.printf('Unit hide : ' + unit.type.name)
        if unit.player == self.enemy:
            self.me.visible_enemy_units.remove(unit)

    def onUnitShow(self, unit):
        #self.game.printf('Unit show : ' + unit.type.name)
        if unit.player == self.enemy:
            self.me.visible_enemy_units.add(unit)

#####################################################################################################

class Battle(object):
    def __init__(self):
        # Add ourselves to the console manager as variable "k"
        pybw.consoleManager.locals.update({'k': self})
        self.MOVE_COEF = 1

    def onConnect(self):
        # Get the game instance
        self.game = getGame() 

    def onMatchStart(self):
        if self.game.isReplay:
            return
        set_basic_information(self, self.game)
        initial_units_scan(self.me, scan_visible_enemy = True, game = self.game)
        self.opt_wta_target_of_weapon = None
        self.write_wta_1_count = 0
        self.write_wta_2_count = 0

    def onSendText(self, message):
        self.message = message

    def onMatchFrame(self):
        frame_count = self.game.frameCount
        #self.game.printf('\x02 ---- Frame Count : ' + str(frame_count) + ' ----')
        self.su = list(self.game.selectedUnits)

        my_army = []
        for key in self.me.units_dictionary.keys():
            if key in self.me.unittype_set_army:
                my_army += list(self.me.units_dictionary[key])
        self.my_army = my_army
        my_enemy = list(self.me.visible_enemy_units)

        if len(my_army) > 0:
            x, y = get_group_center_of(my_army)
            my_army_center = Position(x, y)
            #self.game.drawCircleMap(x, y, 5, COLOR_CYAN)
            #self.game.drawCircleMap(x, y, 6, COLOR_CYAN)
            
        if len(my_enemy) > 0:
            x, y = get_group_center_of(my_enemy)
            my_enemy_center = Position(x, y)
            #self.game.drawCircleMap(x, y, 5, COLOR_MAGENTA)
            #self.game.drawCircleMap(x, y, 6, COLOR_MAGENTA)
            for unit in my_enemy:
                show_hitpoints_of(self.game, unit)
        
        if len(my_army) > 0 and len(my_enemy) > 0:
            if frame_count % 2 == 0:
                self.wta_weapon_units = my_army
                self.wta_target_units = my_enemy
                self.wta_result_1 = opt_wta_step_1(my_army, my_enemy, self, tool = 'openopt')
            else:
                self.opt_wta_target_of_weapon = opt_wta_step_2(self.wta_weapon_units, self.wta_target_units, self, self.wta_result_1)
            #target_list = quick_wta(my_army, my_enemy, move_coef = self.MOVE_COEF)
            if self.opt_wta_target_of_weapon:
                start_attack(self.game, self.wta_weapon_units, self.opt_wta_target_of_weapon, my_army, my_enemy, draw_line_game = True, moving_fire = 'simple')

    def onUnitDestroy(self, unit):
        #self.game.printf('Unit destroy : ' + unit.type.name)
        if unit.player == self.me:
            self.me.units_dictionary[unit.type].remove(unit)

    def onUnitCreate(self, unit):
        pass

    def onUnitMorph(self, unit):
        pass

    def onUnitComplete(self, unit):
        #self.game.printf('Unit complete : ' + unit.type.name)
        if unit.player == self.me:
            try:
                self.me.units_dictionary[unit.type].add(unit)
            except KeyError:
                pass

    def onUnitHide(self, unit):
        #self.game.printf('Unit hide : ' + unit.type.name)
        if unit.player == self.enemy:
            self.me.visible_enemy_units.remove(unit)

    def onUnitShow(self, unit):
        #self.game.printf('Unit show : ' + unit.type.name)
        if unit.player == self.enemy:
            self.me.visible_enemy_units.add(unit)

#####################################################################################################

class OldBattle(object):
    def __init__(self):
        # Add ourselves to the console manager as variable "k"
        pybw.consoleManager.locals.update({'k': self})
        self.MOVE_COEF = 1

    def onConnect(self):
        # Get the game instance
        self.game = getGame() 

    def onMatchStart(self):
        if self.game.isReplay:
            return
        set_basic_information(self, self.game)
        initial_units_scan(self.me, scan_visible_enemy = True, game = self.game)
        

    def onSendText(self, message):
        self.message = message

    def onMatchFrame(self):
        frame_count = self.game.frameCount
        #self.game.printf('\x02 ---- Frame Count : ' + str(frame_count) + ' ----')
        self.su = list(self.game.selectedUnits)

        my_army = []
        for key in self.me.units_dictionary.keys():
            if key in self.me.unittype_set_army:
                my_army += list(self.me.units_dictionary[key])
        self.my_army = my_army
        my_enemy = list(self.me.visible_enemy_units)

        if len(my_army) > 0:
            x, y = get_group_center_of(my_army)
            my_army_center = Position(x, y)
            #self.game.drawCircleMap(x, y, 5, COLOR_CYAN)
            #self.game.drawCircleMap(x, y, 6, COLOR_CYAN)
            
        if len(my_enemy) > 0:
            x, y = get_group_center_of(my_enemy)
            my_enemy_center = Position(x, y)
            #self.game.drawCircleMap(x, y, 5, COLOR_MAGENTA)
            #self.game.drawCircleMap(x, y, 6, COLOR_MAGENTA)
            for unit in my_enemy:
                show_hitpoints_of(self.game, unit)
                
        if len(my_army) > 0 and len(my_enemy) > 0:
            #target_list = quick_wta(my_army, my_enemy, move_coef = self.MOVE_COEF)
            target_list = old_opt_wta(my_army, my_enemy, move_coef = self.MOVE_COEF, game = self.game)
            start_attack(self.game, my_army, target_list, my_army, my_enemy, draw_line_game = True, moving_fire = True)

    def onUnitDestroy(self, unit):
        #self.game.printf('Unit destroy : ' + unit.type.name)
        if unit.player == self.me:
            self.me.units_dictionary[unit.type].remove(unit)

    def onUnitCreate(self, unit):
        pass

    def onUnitMorph(self, unit):
        pass

    def onUnitComplete(self, unit):
        #self.game.printf('Unit complete : ' + unit.type.name)
        if unit.player == self.me:
            try:
                self.me.units_dictionary[unit.type].add(unit)
            except KeyError:
                pass
                
    def onUnitHide(self, unit):
        #self.game.printf('Unit hide : ' + unit.type.name)
        if unit.player == self.enemy:
            self.me.visible_enemy_units.remove(unit)

    def onUnitShow(self, unit):
        #self.game.printf('Unit show : ' + unit.type.name)
        if unit.player == self.enemy:
            self.me.visible_enemy_units.add(unit)