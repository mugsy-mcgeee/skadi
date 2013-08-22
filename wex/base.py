from wex import *


@source('PlayerResource')
class Player(Wex):
  name = valueOf('m_iszPlayerNames')
  #hero = valueOf('m_hSelectedHero').asWex('Hero')


@source('Unit_Hero_*')
class Hero(Wex):
  state = valueOf('DT_DOTA_BaseNPC m_lifeState')

