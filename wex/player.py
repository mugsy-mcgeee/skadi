from wex import *

class Player(Wex):
  id = From('DOTAPlayer').ValueOf('DT_DOTAPlayer m_iPlayerID')

  name = From('PlayerResource').ValueOf('m_iszPlayerNames')
  hero = From('PlayerResource').DataTypeFor('m_hSelectedHero')
