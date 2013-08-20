from wex import *

class Player(Wex):
  hero = Entity('DT_DOTAPlayer').prop('DT_DOTAPlayer m_hAssignedHero').as_dt()

