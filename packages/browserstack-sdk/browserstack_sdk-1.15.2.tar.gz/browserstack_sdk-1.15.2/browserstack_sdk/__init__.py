# coding: UTF-8
import sys
bstack1l1l1111l_opy_ = sys.version_info [0] == 2
bstack1ll11l1ll_opy_ = 2048
bstack1l1ll1lll_opy_ = 7
def bstack1llllll11_opy_ (bstack11lll11_opy_):
    global bstack1l111ll1l_opy_
    bstack1l1ll_opy_ = ord (bstack11lll11_opy_ [-1])
    bstack1l11ll_opy_ = bstack11lll11_opy_ [:-1]
    bstack11l1l1_opy_ = bstack1l1ll_opy_ % len (bstack1l11ll_opy_)
    bstack1ll11l1l1_opy_ = bstack1l11ll_opy_ [:bstack11l1l1_opy_] + bstack1l11ll_opy_ [bstack11l1l1_opy_:]
    if bstack1l1l1111l_opy_:
        bstack11l1llll_opy_ = unicode () .join ([unichr (ord (char) - bstack1ll11l1ll_opy_ - (bstack11l111111_opy_ + bstack1l1ll_opy_) % bstack1l1ll1lll_opy_) for bstack11l111111_opy_, char in enumerate (bstack1ll11l1l1_opy_)])
    else:
        bstack11l1llll_opy_ = str () .join ([chr (ord (char) - bstack1ll11l1ll_opy_ - (bstack11l111111_opy_ + bstack1l1ll_opy_) % bstack1l1ll1lll_opy_) for bstack11l111111_opy_, char in enumerate (bstack1ll11l1l1_opy_)])
    return eval (bstack11l1llll_opy_)
import atexit
import os
import signal
import sys
import time
import yaml
import requests
import logging
import threading
import socket
import datetime
import string
import random
import json
import collections.abc
import re
import multiprocessing
import traceback
import copy
from multiprocessing import Pool
from packaging import version
from browserstack.local import Local
from urllib.parse import urlparse
bstack111l11l1_opy_ = {
	bstack1llllll11_opy_ (u"ࠫࡺࡹࡥࡳࡐࡤࡱࡪ࠭ࠀ"): bstack1llllll11_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡺࡹࡥࡳࠩࠁ"),
  bstack1llllll11_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸࡑࡥࡺࠩࠂ"): bstack1llllll11_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴࡫ࡦࡻࠪࠃ"),
  bstack1llllll11_opy_ (u"ࠨࡱࡶ࡚ࡪࡸࡳࡪࡱࡱࠫࠄ"): bstack1llllll11_opy_ (u"ࠩࡲࡷࡤࡼࡥࡳࡵ࡬ࡳࡳ࠭ࠅ"),
  bstack1llllll11_opy_ (u"ࠪࡹࡸ࡫ࡗ࠴ࡅࠪࠆ"): bstack1llllll11_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡹࡸ࡫࡟ࡸ࠵ࡦࠫࠇ"),
  bstack1llllll11_opy_ (u"ࠬࡶࡲࡰ࡬ࡨࡧࡹࡔࡡ࡮ࡧࠪࠈ"): bstack1llllll11_opy_ (u"࠭ࡰࡳࡱ࡭ࡩࡨࡺࠧࠉ"),
  bstack1llllll11_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡔࡡ࡮ࡧࠪࠊ"): bstack1llllll11_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࠧࠋ"),
  bstack1llllll11_opy_ (u"ࠩࡶࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧࠌ"): bstack1llllll11_opy_ (u"ࠪࡲࡦࡳࡥࠨࠍ"),
  bstack1llllll11_opy_ (u"ࠫࡩ࡫ࡢࡶࡩࠪࠎ"): bstack1llllll11_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡩ࡫ࡢࡶࡩࠪࠏ"),
  bstack1llllll11_opy_ (u"࠭ࡣࡰࡰࡶࡳࡱ࡫ࡌࡰࡩࡶࠫࠐ"): bstack1llllll11_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡣࡰࡰࡶࡳࡱ࡫ࠧࠑ"),
  bstack1llllll11_opy_ (u"ࠨࡰࡨࡸࡼࡵࡲ࡬ࡎࡲ࡫ࡸ࠭ࠒ"): bstack1llllll11_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡰࡨࡸࡼࡵࡲ࡬ࡎࡲ࡫ࡸ࠭ࠓ"),
  bstack1llllll11_opy_ (u"ࠪࡥࡵࡶࡩࡶ࡯ࡏࡳ࡬ࡹࠧࠔ"): bstack1llllll11_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡥࡵࡶࡩࡶ࡯ࡏࡳ࡬ࡹࠧࠕ"),
  bstack1llllll11_opy_ (u"ࠬࡼࡩࡥࡧࡲࠫࠖ"): bstack1llllll11_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡼࡩࡥࡧࡲࠫࠗ"),
  bstack1llllll11_opy_ (u"ࠧࡴࡧ࡯ࡩࡳ࡯ࡵ࡮ࡎࡲ࡫ࡸ࠭࠘"): bstack1llllll11_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡴࡧ࡯ࡩࡳ࡯ࡵ࡮ࡎࡲ࡫ࡸ࠭࠙"),
  bstack1llllll11_opy_ (u"ࠩࡷࡩࡱ࡫࡭ࡦࡶࡵࡽࡑࡵࡧࡴࠩࠚ"): bstack1llllll11_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡷࡩࡱ࡫࡭ࡦࡶࡵࡽࡑࡵࡧࡴࠩࠛ"),
  bstack1llllll11_opy_ (u"ࠫ࡬࡫࡯ࡍࡱࡦࡥࡹ࡯࡯࡯ࠩࠜ"): bstack1llllll11_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲࡬࡫࡯ࡍࡱࡦࡥࡹ࡯࡯࡯ࠩࠝ"),
  bstack1llllll11_opy_ (u"࠭ࡴࡪ࡯ࡨࡾࡴࡴࡥࠨࠞ"): bstack1llllll11_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡴࡪ࡯ࡨࡾࡴࡴࡥࠨࠟ"),
  bstack1llllll11_opy_ (u"ࠨࡵࡨࡰࡪࡴࡩࡶ࡯࡙ࡩࡷࡹࡩࡰࡰࠪࠠ"): bstack1llllll11_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡵࡨࡰࡪࡴࡩࡶ࡯ࡢࡺࡪࡸࡳࡪࡱࡱࠫࠡ"),
  bstack1llllll11_opy_ (u"ࠪࡱࡦࡹ࡫ࡄࡱࡰࡱࡦࡴࡤࡴࠩࠢ"): bstack1llllll11_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡱࡦࡹ࡫ࡄࡱࡰࡱࡦࡴࡤࡴࠩࠣ"),
  bstack1llllll11_opy_ (u"ࠬ࡯ࡤ࡭ࡧࡗ࡭ࡲ࡫࡯ࡶࡶࠪࠤ"): bstack1llllll11_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳࡯ࡤ࡭ࡧࡗ࡭ࡲ࡫࡯ࡶࡶࠪࠥ"),
  bstack1llllll11_opy_ (u"ࠧ࡮ࡣࡶ࡯ࡇࡧࡳࡪࡥࡄࡹࡹ࡮ࠧࠦ"): bstack1llllll11_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮࡮ࡣࡶ࡯ࡇࡧࡳࡪࡥࡄࡹࡹ࡮ࠧࠧ"),
  bstack1llllll11_opy_ (u"ࠩࡶࡩࡳࡪࡋࡦࡻࡶࠫࠨ"): bstack1llllll11_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡶࡩࡳࡪࡋࡦࡻࡶࠫࠩ"),
  bstack1llllll11_opy_ (u"ࠫࡦࡻࡴࡰ࡙ࡤ࡭ࡹ࠭ࠪ"): bstack1llllll11_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡦࡻࡴࡰ࡙ࡤ࡭ࡹ࠭ࠫ"),
  bstack1llllll11_opy_ (u"࠭ࡨࡰࡵࡷࡷࠬࠬ"): bstack1llllll11_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡨࡰࡵࡷࡷࠬ࠭"),
  bstack1llllll11_opy_ (u"ࠨࡤࡩࡧࡦࡩࡨࡦࠩ࠮"): bstack1llllll11_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡤࡩࡧࡦࡩࡨࡦࠩ࠯"),
  bstack1llllll11_opy_ (u"ࠪࡻࡸࡒ࡯ࡤࡣ࡯ࡗࡺࡶࡰࡰࡴࡷࠫ࠰"): bstack1llllll11_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡻࡸࡒ࡯ࡤࡣ࡯ࡗࡺࡶࡰࡰࡴࡷࠫ࠱"),
  bstack1llllll11_opy_ (u"ࠬࡪࡩࡴࡣࡥࡰࡪࡉ࡯ࡳࡵࡕࡩࡸࡺࡲࡪࡥࡷ࡭ࡴࡴࡳࠨ࠲"): bstack1llllll11_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡪࡩࡴࡣࡥࡰࡪࡉ࡯ࡳࡵࡕࡩࡸࡺࡲࡪࡥࡷ࡭ࡴࡴࡳࠨ࠳"),
  bstack1llllll11_opy_ (u"ࠧࡥࡧࡹ࡭ࡨ࡫ࡎࡢ࡯ࡨࠫ࠴"): bstack1llllll11_opy_ (u"ࠨࡦࡨࡺ࡮ࡩࡥࠨ࠵"),
  bstack1llllll11_opy_ (u"ࠩࡵࡩࡦࡲࡍࡰࡤ࡬ࡰࡪ࠭࠶"): bstack1llllll11_opy_ (u"ࠪࡶࡪࡧ࡬ࡠ࡯ࡲࡦ࡮ࡲࡥࠨ࠷"),
  bstack1llllll11_opy_ (u"ࠫࡦࡶࡰࡪࡷࡰ࡚ࡪࡸࡳࡪࡱࡱࠫ࠸"): bstack1llllll11_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡦࡶࡰࡪࡷࡰࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬ࠹"),
  bstack1llllll11_opy_ (u"࠭ࡣࡶࡵࡷࡳࡲࡔࡥࡵࡹࡲࡶࡰ࠭࠺"): bstack1llllll11_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡣࡶࡵࡷࡳࡲࡔࡥࡵࡹࡲࡶࡰ࠭࠻"),
  bstack1llllll11_opy_ (u"ࠨࡰࡨࡸࡼࡵࡲ࡬ࡒࡵࡳ࡫࡯࡬ࡦࠩ࠼"): bstack1llllll11_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡰࡨࡸࡼࡵࡲ࡬ࡒࡵࡳ࡫࡯࡬ࡦࠩ࠽"),
  bstack1llllll11_opy_ (u"ࠪࡥࡨࡩࡥࡱࡶࡌࡲࡸ࡫ࡣࡶࡴࡨࡇࡪࡸࡴࡴࠩ࠾"): bstack1llllll11_opy_ (u"ࠫࡦࡩࡣࡦࡲࡷࡗࡸࡲࡃࡦࡴࡷࡷࠬ࠿"),
  bstack1llllll11_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡗࡉࡑࠧࡀ"): bstack1llllll11_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡗࡉࡑࠧࡁ"),
  bstack1llllll11_opy_ (u"ࠧࡴࡱࡸࡶࡨ࡫ࠧࡂ"): bstack1llllll11_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡴࡱࡸࡶࡨ࡫ࠧࡃ"),
  bstack1llllll11_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫࡄ"): bstack1llllll11_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫࡅ"),
  bstack1llllll11_opy_ (u"ࠫ࡭ࡵࡳࡵࡐࡤࡱࡪ࠭ࡆ"): bstack1llllll11_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲࡭ࡵࡳࡵࡐࡤࡱࡪ࠭ࡇ"),
}
bstack11l1l11ll_opy_ = [
  bstack1llllll11_opy_ (u"࠭࡯ࡴࠩࡈ"),
  bstack1llllll11_opy_ (u"ࠧࡰࡵ࡙ࡩࡷࡹࡩࡰࡰࠪࡉ"),
  bstack1llllll11_opy_ (u"ࠨࡵࡨࡰࡪࡴࡩࡶ࡯࡙ࡩࡷࡹࡩࡰࡰࠪࡊ"),
  bstack1llllll11_opy_ (u"ࠩࡶࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧࡋ"),
  bstack1llllll11_opy_ (u"ࠪࡨࡪࡼࡩࡤࡧࡑࡥࡲ࡫ࠧࡌ"),
  bstack1llllll11_opy_ (u"ࠫࡷ࡫ࡡ࡭ࡏࡲࡦ࡮ࡲࡥࠨࡍ"),
  bstack1llllll11_opy_ (u"ࠬࡧࡰࡱ࡫ࡸࡱ࡛࡫ࡲࡴ࡫ࡲࡲࠬࡎ"),
]
bstack11lll11l1_opy_ = {
  bstack1llllll11_opy_ (u"࠭ࡵࡴࡧࡵࡒࡦࡳࡥࠨࡏ"): [bstack1llllll11_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡕࡔࡇࡕࡒࡆࡓࡅࠨࡐ"), bstack1llllll11_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡖࡕࡈࡖࡤࡔࡁࡎࡇࠪࡑ")],
  bstack1llllll11_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴࡍࡨࡽࠬࡒ"): bstack1llllll11_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡄࡇࡈࡋࡓࡔࡡࡎࡉ࡞࠭ࡓ"),
  bstack1llllll11_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠧࡔ"): bstack1llllll11_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡇ࡛ࡉࡍࡆࡢࡒࡆࡓࡅࠨࡕ"),
  bstack1llllll11_opy_ (u"࠭ࡰࡳࡱ࡭ࡩࡨࡺࡎࡢ࡯ࡨࠫࡖ"): bstack1llllll11_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡐࡓࡑࡍࡉࡈ࡚࡟ࡏࡃࡐࡉࠬࡗ"),
  bstack1llllll11_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪࡘ"): bstack1llllll11_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡄࡘࡍࡑࡊ࡟ࡊࡆࡈࡒ࡙ࡏࡆࡊࡇࡕ࡙ࠫ"),
  bstack1llllll11_opy_ (u"ࠪࡴࡦࡸࡡ࡭࡮ࡨࡰࡸࡖࡥࡳࡒ࡯ࡥࡹ࡬࡯ࡳ࡯࡚ࠪ"): bstack1llllll11_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡔࡆࡘࡁࡍࡎࡈࡐࡘࡥࡐࡆࡔࡢࡔࡑࡇࡔࡇࡑࡕࡑ࡛ࠬ"),
  bstack1llllll11_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࠩ࡜"): bstack1llllll11_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡒࡏࡄࡃࡏࠫ࡝"),
  bstack1llllll11_opy_ (u"ࠧࡳࡧࡵࡹࡳ࡚ࡥࡴࡶࡶࠫ࡞"): bstack1llllll11_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡓࡇࡕ࡙ࡓࡥࡔࡆࡕࡗࡗࠬ࡟"),
  bstack1llllll11_opy_ (u"ࠩࡤࡴࡵ࠭ࡠ"): [bstack1llllll11_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡄࡔࡕࡥࡉࡅࠩࡡ"), bstack1llllll11_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡅࡕࡖࠧࡢ")],
  bstack1llllll11_opy_ (u"ࠬࡲ࡯ࡨࡎࡨࡺࡪࡲࠧࡣ"): bstack1llllll11_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡕࡂࡔࡇࡕ࡚ࡆࡈࡉࡍࡋࡗ࡝ࡤࡊࡅࡃࡗࡊࠫࡤ"),
  bstack1llllll11_opy_ (u"ࠧࡢࡷࡷࡳࡲࡧࡴࡪࡱࡱࠫࡥ"): bstack1llllll11_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡂࡗࡗࡓࡒࡇࡔࡊࡑࡑࠫࡦ")
}
bstack11ll111l1_opy_ = {
  bstack1llllll11_opy_ (u"ࠩࡸࡷࡪࡸࡎࡢ࡯ࡨࠫࡧ"): [bstack1llllll11_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡸࡷࡪࡸ࡟࡯ࡣࡰࡩࠬࡨ"), bstack1llllll11_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡹࡸ࡫ࡲࡏࡣࡰࡩࠬࡩ")],
  bstack1llllll11_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷࡐ࡫ࡹࠨࡪ"): [bstack1llllll11_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡧࡣࡤࡧࡶࡷࡤࡱࡥࡺࠩ࡫"), bstack1llllll11_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡡࡤࡥࡨࡷࡸࡑࡥࡺࠩ࡬")],
  bstack1llllll11_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫ࡭"): bstack1llllll11_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫ࡮"),
  bstack1llllll11_opy_ (u"ࠪࡴࡷࡵࡪࡦࡥࡷࡒࡦࡳࡥࠨ࡯"): bstack1llllll11_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡴࡷࡵࡪࡦࡥࡷࡒࡦࡳࡥࠨࡰ"),
  bstack1llllll11_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧࡱ"): bstack1llllll11_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧࡲ"),
  bstack1llllll11_opy_ (u"ࠧࡱࡣࡵࡥࡱࡲࡥ࡭ࡵࡓࡩࡷࡖ࡬ࡢࡶࡩࡳࡷࡳࠧࡳ"): [bstack1llllll11_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡱࡲࡳࠫࡴ"), bstack1llllll11_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡲࡤࡶࡦࡲ࡬ࡦ࡮ࡶࡔࡪࡸࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨࡵ")],
  bstack1llllll11_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࠧࡶ"): bstack1llllll11_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡰࡴࡩࡡ࡭ࠩࡷ"),
  bstack1llllll11_opy_ (u"ࠬࡸࡥࡳࡷࡱࡘࡪࡹࡴࡴࠩࡸ"): bstack1llllll11_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡸࡥࡳࡷࡱࡘࡪࡹࡴࡴࠩࡹ"),
  bstack1llllll11_opy_ (u"ࠧࡢࡲࡳࠫࡺ"): bstack1llllll11_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡢࡲࡳࠫࡻ"),
  bstack1llllll11_opy_ (u"ࠩ࡯ࡳ࡬ࡒࡥࡷࡧ࡯ࠫࡼ"): bstack1llllll11_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰࡯ࡳ࡬ࡒࡥࡷࡧ࡯ࠫࡽ"),
  bstack1llllll11_opy_ (u"ࠫࡦࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠨࡾ"): bstack1llllll11_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡦࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠨࡿ")
}
bstack1l1l1l1ll_opy_ = {
  bstack1llllll11_opy_ (u"࠭࡯ࡴࡘࡨࡶࡸ࡯࡯࡯ࠩࢀ"): bstack1llllll11_opy_ (u"ࠧࡰࡵࡢࡺࡪࡸࡳࡪࡱࡱࠫࢁ"),
  bstack1llllll11_opy_ (u"ࠨࡵࡨࡰࡪࡴࡩࡶ࡯࡙ࡩࡷࡹࡩࡰࡰࠪࢂ"): [bstack1llllll11_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡵࡨࡰࡪࡴࡩࡶ࡯ࡢࡺࡪࡸࡳࡪࡱࡱࠫࢃ"), bstack1llllll11_opy_ (u"ࠪࡷࡪࡲࡥ࡯࡫ࡸࡱࡤࡼࡥࡳࡵ࡬ࡳࡳ࠭ࢄ")],
  bstack1llllll11_opy_ (u"ࠫࡸ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠩࢅ"): bstack1llllll11_opy_ (u"ࠬࡴࡡ࡮ࡧࠪࢆ"),
  bstack1llllll11_opy_ (u"࠭ࡤࡦࡸ࡬ࡧࡪࡔࡡ࡮ࡧࠪࢇ"): bstack1llllll11_opy_ (u"ࠧࡥࡧࡹ࡭ࡨ࡫ࠧ࢈"),
  bstack1llllll11_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡐࡤࡱࡪ࠭ࢉ"): [bstack1llllll11_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࠪࢊ"), bstack1llllll11_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡣࡳࡧ࡭ࡦࠩࢋ")],
  bstack1llllll11_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶ࡛࡫ࡲࡴ࡫ࡲࡲࠬࢌ"): bstack1llllll11_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡥࡶࡦࡴࡶ࡭ࡴࡴࠧࢍ"),
  bstack1llllll11_opy_ (u"࠭ࡲࡦࡣ࡯ࡑࡴࡨࡩ࡭ࡧࠪࢎ"): bstack1llllll11_opy_ (u"ࠧࡳࡧࡤࡰࡤࡳ࡯ࡣ࡫࡯ࡩࠬ࢏"),
  bstack1llllll11_opy_ (u"ࠨࡣࡳࡴ࡮ࡻ࡭ࡗࡧࡵࡷ࡮ࡵ࡮ࠨ࢐"): [bstack1llllll11_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡣࡳࡴ࡮ࡻ࡭ࡠࡸࡨࡶࡸ࡯࡯࡯ࠩ࢑"), bstack1llllll11_opy_ (u"ࠪࡥࡵࡶࡩࡶ࡯ࡢࡺࡪࡸࡳࡪࡱࡱࠫ࢒")],
  bstack1llllll11_opy_ (u"ࠫࡦࡩࡣࡦࡲࡷࡍࡳࡹࡥࡤࡷࡵࡩࡈ࡫ࡲࡵࡵࠪ࢓"): [bstack1llllll11_opy_ (u"ࠬࡧࡣࡤࡧࡳࡸࡘࡹ࡬ࡄࡧࡵࡸࡸ࠭࢔"), bstack1llllll11_opy_ (u"࠭ࡡࡤࡥࡨࡴࡹ࡙ࡳ࡭ࡅࡨࡶࡹ࠭࢕")]
}
bstack1llllll_opy_ = [
  bstack1llllll11_opy_ (u"ࠧࡢࡥࡦࡩࡵࡺࡉ࡯ࡵࡨࡧࡺࡸࡥࡄࡧࡵࡸࡸ࠭࢖"),
  bstack1llllll11_opy_ (u"ࠨࡲࡤ࡫ࡪࡒ࡯ࡢࡦࡖࡸࡷࡧࡴࡦࡩࡼࠫࢗ"),
  bstack1llllll11_opy_ (u"ࠩࡳࡶࡴࡾࡹࠨ࢘"),
  bstack1llllll11_opy_ (u"ࠪࡷࡪࡺࡗࡪࡰࡧࡳࡼࡘࡥࡤࡶ࢙ࠪ"),
  bstack1llllll11_opy_ (u"ࠫࡹ࡯࡭ࡦࡱࡸࡸࡸ࢚࠭"),
  bstack1llllll11_opy_ (u"ࠬࡹࡴࡳ࡫ࡦࡸࡋ࡯࡬ࡦࡋࡱࡸࡪࡸࡡࡤࡶࡤࡦ࡮ࡲࡩࡵࡻ࢛ࠪ"),
  bstack1llllll11_opy_ (u"࠭ࡵ࡯ࡪࡤࡲࡩࡲࡥࡥࡒࡵࡳࡲࡶࡴࡃࡧ࡫ࡥࡻ࡯࡯ࡳࠩ࢜"),
  bstack1llllll11_opy_ (u"ࠧࡨࡱࡲ࡫࠿ࡩࡨࡳࡱࡰࡩࡔࡶࡴࡪࡱࡱࡷࠬ࢝"),
  bstack1llllll11_opy_ (u"ࠨ࡯ࡲࡾ࠿࡬ࡩࡳࡧࡩࡳࡽࡕࡰࡵ࡫ࡲࡲࡸ࠭࢞"),
  bstack1llllll11_opy_ (u"ࠩࡰࡷ࠿࡫ࡤࡨࡧࡒࡴࡹ࡯࡯࡯ࡵࠪ࢟"),
  bstack1llllll11_opy_ (u"ࠪࡷࡪࡀࡩࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩࢠ"),
  bstack1llllll11_opy_ (u"ࠫࡸࡧࡦࡢࡴ࡬࠲ࡴࡶࡴࡪࡱࡱࡷࠬࢡ"),
]
bstack11ll1l11l_opy_ = [
  bstack1llllll11_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࠩࢢ"),
  bstack1llllll11_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪࢣ"),
  bstack1llllll11_opy_ (u"ࠧ࡭ࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭ࢤ"),
  bstack1llllll11_opy_ (u"ࠨࡲࡤࡶࡦࡲ࡬ࡦ࡮ࡶࡔࡪࡸࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨࢥ"),
  bstack1llllll11_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬࢦ"),
  bstack1llllll11_opy_ (u"ࠪࡰࡴ࡭ࡌࡦࡸࡨࡰࠬࢧ"),
  bstack1llllll11_opy_ (u"ࠫ࡭ࡺࡴࡱࡒࡵࡳࡽࡿࠧࢨ"),
  bstack1llllll11_opy_ (u"ࠬ࡮ࡴࡵࡲࡶࡔࡷࡵࡸࡺࠩࢩ"),
  bstack1llllll11_opy_ (u"࠭ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࠩࢪ"),
  bstack1llllll11_opy_ (u"ࠧࡵࡧࡶࡸࡈࡵ࡮ࡵࡧࡻࡸࡔࡶࡴࡪࡱࡱࡷࠬࢫ")
]
bstack11l1l1111_opy_ = [
  bstack1llllll11_opy_ (u"ࠨࡷࡳࡰࡴࡧࡤࡎࡧࡧ࡭ࡦ࠭ࢬ"),
  bstack1llllll11_opy_ (u"ࠩࡸࡷࡪࡸࡎࡢ࡯ࡨࠫࢭ"),
  bstack1llllll11_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵࡎࡩࡾ࠭ࢮ"),
  bstack1llllll11_opy_ (u"ࠫࡸ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠩࢯ"),
  bstack1llllll11_opy_ (u"ࠬࡺࡥࡴࡶࡓࡶ࡮ࡵࡲࡪࡶࡼࠫࢰ"),
  bstack1llllll11_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦࠩࢱ"),
  bstack1llllll11_opy_ (u"ࠧࡣࡷ࡬ࡰࡩ࡚ࡡࡨࠩࢲ"),
  bstack1llllll11_opy_ (u"ࠨࡲࡵࡳ࡯࡫ࡣࡵࡐࡤࡱࡪ࠭ࢳ"),
  bstack1llllll11_opy_ (u"ࠩࡶࡩࡱ࡫࡮ࡪࡷࡰ࡚ࡪࡸࡳࡪࡱࡱࠫࢴ"),
  bstack1llllll11_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡒࡦࡳࡥࠨࢵ"),
  bstack1llllll11_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶ࡛࡫ࡲࡴ࡫ࡲࡲࠬࢶ"),
  bstack1llllll11_opy_ (u"ࠬࡲ࡯ࡤࡣ࡯ࠫࢷ"),
  bstack1llllll11_opy_ (u"࠭࡯ࡴࠩࢸ"),
  bstack1llllll11_opy_ (u"ࠧࡰࡵ࡙ࡩࡷࡹࡩࡰࡰࠪࢹ"),
  bstack1llllll11_opy_ (u"ࠨࡪࡲࡷࡹࡹࠧࢺ"),
  bstack1llllll11_opy_ (u"ࠩࡤࡹࡹࡵࡗࡢ࡫ࡷࠫࢻ"),
  bstack1llllll11_opy_ (u"ࠪࡶࡪ࡭ࡩࡰࡰࠪࢼ"),
  bstack1llllll11_opy_ (u"ࠫࡹ࡯࡭ࡦࡼࡲࡲࡪ࠭ࢽ"),
  bstack1llllll11_opy_ (u"ࠬࡳࡡࡤࡪ࡬ࡲࡪ࠭ࢾ"),
  bstack1llllll11_opy_ (u"࠭ࡲࡦࡵࡲࡰࡺࡺࡩࡰࡰࠪࢿ"),
  bstack1llllll11_opy_ (u"ࠧࡪࡦ࡯ࡩ࡙࡯࡭ࡦࡱࡸࡸࠬࣀ"),
  bstack1llllll11_opy_ (u"ࠨࡦࡨࡺ࡮ࡩࡥࡐࡴ࡬ࡩࡳࡺࡡࡵ࡫ࡲࡲࠬࣁ"),
  bstack1llllll11_opy_ (u"ࠩࡹ࡭ࡩ࡫࡯ࠨࣂ"),
  bstack1llllll11_opy_ (u"ࠪࡲࡴࡖࡡࡨࡧࡏࡳࡦࡪࡔࡪ࡯ࡨࡳࡺࡺࠧࣃ"),
  bstack1llllll11_opy_ (u"ࠫࡧ࡬ࡣࡢࡥ࡫ࡩࠬࣄ"),
  bstack1llllll11_opy_ (u"ࠬࡪࡥࡣࡷࡪࠫࣅ"),
  bstack1llllll11_opy_ (u"࠭ࡣࡶࡵࡷࡳࡲ࡙ࡣࡳࡧࡨࡲࡸ࡮࡯ࡵࡵࠪࣆ"),
  bstack1llllll11_opy_ (u"ࠧࡤࡷࡶࡸࡴࡳࡓࡦࡰࡧࡏࡪࡿࡳࠨࣇ"),
  bstack1llllll11_opy_ (u"ࠨࡴࡨࡥࡱࡓ࡯ࡣ࡫࡯ࡩࠬࣈ"),
  bstack1llllll11_opy_ (u"ࠩࡱࡳࡕ࡯ࡰࡦ࡮࡬ࡲࡪ࠭ࣉ"),
  bstack1llllll11_opy_ (u"ࠪࡧ࡭࡫ࡣ࡬ࡗࡕࡐࠬ࣊"),
  bstack1llllll11_opy_ (u"ࠫࡱࡵࡣࡢ࡮ࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭࣋"),
  bstack1llllll11_opy_ (u"ࠬࡧࡣࡤࡧࡳࡸࡈࡵ࡯࡬࡫ࡨࡷࠬ࣌"),
  bstack1llllll11_opy_ (u"࠭ࡣࡢࡲࡷࡹࡷ࡫ࡃࡳࡣࡶ࡬ࠬ࣍"),
  bstack1llllll11_opy_ (u"ࠧࡥࡧࡹ࡭ࡨ࡫ࡎࡢ࡯ࡨࠫ࣎"),
  bstack1llllll11_opy_ (u"ࠨࡣࡳࡴ࡮ࡻ࡭ࡗࡧࡵࡷ࡮ࡵ࡮ࠨ࣏"),
  bstack1llllll11_opy_ (u"ࠩࡤࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳ࡜ࡥࡳࡵ࡬ࡳࡳ࣐࠭"),
  bstack1llllll11_opy_ (u"ࠪࡲࡴࡈ࡬ࡢࡰ࡮ࡔࡴࡲ࡬ࡪࡰࡪ࣑ࠫ"),
  bstack1llllll11_opy_ (u"ࠫࡲࡧࡳ࡬ࡕࡨࡲࡩࡑࡥࡺࡵ࣒ࠪ"),
  bstack1llllll11_opy_ (u"ࠬࡪࡥࡷ࡫ࡦࡩࡑࡵࡧࡴ࣓ࠩ"),
  bstack1llllll11_opy_ (u"࠭ࡤࡦࡸ࡬ࡧࡪࡏࡤࠨࣔ"),
  bstack1llllll11_opy_ (u"ࠧࡥࡧࡧ࡭ࡨࡧࡴࡦࡦࡇࡩࡻ࡯ࡣࡦࠩࣕ"),
  bstack1llllll11_opy_ (u"ࠨࡪࡨࡥࡩ࡫ࡲࡑࡣࡵࡥࡲࡹࠧࣖ"),
  bstack1llllll11_opy_ (u"ࠩࡳ࡬ࡴࡴࡥࡏࡷࡰࡦࡪࡸࠧࣗ"),
  bstack1llllll11_opy_ (u"ࠪࡲࡪࡺࡷࡰࡴ࡮ࡐࡴ࡭ࡳࠨࣘ"),
  bstack1llllll11_opy_ (u"ࠫࡳ࡫ࡴࡸࡱࡵ࡯ࡑࡵࡧࡴࡑࡳࡸ࡮ࡵ࡮ࡴࠩࣙ"),
  bstack1llllll11_opy_ (u"ࠬࡩ࡯࡯ࡵࡲࡰࡪࡒ࡯ࡨࡵࠪࣚ"),
  bstack1llllll11_opy_ (u"࠭ࡵࡴࡧ࡚࠷ࡈ࠭ࣛ"),
  bstack1llllll11_opy_ (u"ࠧࡢࡲࡳ࡭ࡺࡳࡌࡰࡩࡶࠫࣜ"),
  bstack1llllll11_opy_ (u"ࠨࡧࡱࡥࡧࡲࡥࡃ࡫ࡲࡱࡪࡺࡲࡪࡥࠪࣝ"),
  bstack1llllll11_opy_ (u"ࠩࡹ࡭ࡩ࡫࡯ࡗ࠴ࠪࣞ"),
  bstack1llllll11_opy_ (u"ࠪࡱ࡮ࡪࡓࡦࡵࡶ࡭ࡴࡴࡉ࡯ࡵࡷࡥࡱࡲࡁࡱࡲࡶࠫࣟ"),
  bstack1llllll11_opy_ (u"ࠫࡪࡹࡰࡳࡧࡶࡷࡴ࡙ࡥࡳࡸࡨࡶࠬ࣠"),
  bstack1llllll11_opy_ (u"ࠬࡹࡥ࡭ࡧࡱ࡭ࡺࡳࡌࡰࡩࡶࠫ࣡"),
  bstack1llllll11_opy_ (u"࠭ࡳࡦ࡮ࡨࡲ࡮ࡻ࡭ࡄࡦࡳࠫ࣢"),
  bstack1llllll11_opy_ (u"ࠧࡵࡧ࡯ࡩࡲ࡫ࡴࡳࡻࡏࡳ࡬ࡹࣣࠧ"),
  bstack1llllll11_opy_ (u"ࠨࡵࡼࡲࡨ࡚ࡩ࡮ࡧ࡚࡭ࡹ࡮ࡎࡕࡒࠪࣤ"),
  bstack1llllll11_opy_ (u"ࠩࡪࡩࡴࡒ࡯ࡤࡣࡷ࡭ࡴࡴࠧࣥ"),
  bstack1llllll11_opy_ (u"ࠪ࡫ࡵࡹࡌࡰࡥࡤࡸ࡮ࡵ࡮ࠨࣦ"),
  bstack1llllll11_opy_ (u"ࠫࡳ࡫ࡴࡸࡱࡵ࡯ࡕࡸ࡯ࡧ࡫࡯ࡩࠬࣧ"),
  bstack1llllll11_opy_ (u"ࠬࡩࡵࡴࡶࡲࡱࡓ࡫ࡴࡸࡱࡵ࡯ࠬࣨ"),
  bstack1llllll11_opy_ (u"࠭ࡦࡰࡴࡦࡩࡈ࡮ࡡ࡯ࡩࡨࡎࡦࡸࣩࠧ"),
  bstack1llllll11_opy_ (u"ࠧࡹ࡯ࡶࡎࡦࡸࠧ࣪"),
  bstack1llllll11_opy_ (u"ࠨࡺࡰࡼࡏࡧࡲࠨ࣫"),
  bstack1llllll11_opy_ (u"ࠩࡰࡥࡸࡱࡃࡰ࡯ࡰࡥࡳࡪࡳࠨ࣬"),
  bstack1llllll11_opy_ (u"ࠪࡱࡦࡹ࡫ࡃࡣࡶ࡭ࡨࡇࡵࡵࡪ࣭ࠪ"),
  bstack1llllll11_opy_ (u"ࠫࡼࡹࡌࡰࡥࡤࡰࡘࡻࡰࡱࡱࡵࡸ࣮ࠬ"),
  bstack1llllll11_opy_ (u"ࠬࡪࡩࡴࡣࡥࡰࡪࡉ࡯ࡳࡵࡕࡩࡸࡺࡲࡪࡥࡷ࡭ࡴࡴࡳࠨ࣯"),
  bstack1llllll11_opy_ (u"࠭ࡡࡱࡲ࡙ࡩࡷࡹࡩࡰࡰࣰࠪ"),
  bstack1llllll11_opy_ (u"ࠧࡢࡥࡦࡩࡵࡺࡉ࡯ࡵࡨࡧࡺࡸࡥࡄࡧࡵࡸࡸࣱ࠭"),
  bstack1llllll11_opy_ (u"ࠨࡴࡨࡷ࡮࡭࡮ࡂࡲࡳࣲࠫ"),
  bstack1llllll11_opy_ (u"ࠩࡧ࡭ࡸࡧࡢ࡭ࡧࡄࡲ࡮ࡳࡡࡵ࡫ࡲࡲࡸ࠭ࣳ"),
  bstack1llllll11_opy_ (u"ࠪࡧࡦࡴࡡࡳࡻࠪࣴ"),
  bstack1llllll11_opy_ (u"ࠫ࡫࡯ࡲࡦࡨࡲࡼࠬࣵ"),
  bstack1llllll11_opy_ (u"ࠬࡩࡨࡳࡱࡰࡩࣶࠬ"),
  bstack1llllll11_opy_ (u"࠭ࡩࡦࠩࣷ"),
  bstack1llllll11_opy_ (u"ࠧࡦࡦࡪࡩࠬࣸ"),
  bstack1llllll11_opy_ (u"ࠨࡵࡤࡪࡦࡸࡩࠨࣹ"),
  bstack1llllll11_opy_ (u"ࠩࡴࡹࡪࡻࡥࠨࣺ"),
  bstack1llllll11_opy_ (u"ࠪ࡭ࡳࡺࡥࡳࡰࡤࡰࠬࣻ"),
  bstack1llllll11_opy_ (u"ࠫࡦࡶࡰࡔࡶࡲࡶࡪࡉ࡯࡯ࡨ࡬࡫ࡺࡸࡡࡵ࡫ࡲࡲࠬࣼ"),
  bstack1llllll11_opy_ (u"ࠬ࡫࡮ࡢࡤ࡯ࡩࡈࡧ࡭ࡦࡴࡤࡍࡲࡧࡧࡦࡋࡱ࡮ࡪࡩࡴࡪࡱࡱࠫࣽ"),
  bstack1llllll11_opy_ (u"࠭࡮ࡦࡶࡺࡳࡷࡱࡌࡰࡩࡶࡉࡽࡩ࡬ࡶࡦࡨࡌࡴࡹࡴࡴࠩࣾ"),
  bstack1llllll11_opy_ (u"ࠧ࡯ࡧࡷࡻࡴࡸ࡫ࡍࡱࡪࡷࡎࡴࡣ࡭ࡷࡧࡩࡍࡵࡳࡵࡵࠪࣿ"),
  bstack1llllll11_opy_ (u"ࠨࡷࡳࡨࡦࡺࡥࡂࡲࡳࡗࡪࡺࡴࡪࡰࡪࡷࠬऀ"),
  bstack1llllll11_opy_ (u"ࠩࡵࡩࡸ࡫ࡲࡷࡧࡇࡩࡻ࡯ࡣࡦࠩँ"),
  bstack1llllll11_opy_ (u"ࠪࡷࡴࡻࡲࡤࡧࠪं"),
  bstack1llllll11_opy_ (u"ࠫࡸ࡫࡮ࡥࡍࡨࡽࡸ࠭ः"),
  bstack1llllll11_opy_ (u"ࠬ࡫࡮ࡢࡤ࡯ࡩࡕࡧࡳࡴࡥࡲࡨࡪ࠭ऄ"),
  bstack1llllll11_opy_ (u"࠭ࡵࡱࡦࡤࡸࡪࡏ࡯ࡴࡆࡨࡺ࡮ࡩࡥࡔࡧࡷࡸ࡮ࡴࡧࡴࠩअ"),
  bstack1llllll11_opy_ (u"ࠧࡦࡰࡤࡦࡱ࡫ࡁࡶࡦ࡬ࡳࡎࡴࡪࡦࡥࡷ࡭ࡴࡴࠧआ"),
  bstack1llllll11_opy_ (u"ࠨࡧࡱࡥࡧࡲࡥࡂࡲࡳࡰࡪࡖࡡࡺࠩइ"),
  bstack1llllll11_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࠪई"),
  bstack1llllll11_opy_ (u"ࠪࡻࡩ࡯࡯ࡔࡧࡵࡺ࡮ࡩࡥࠨउ"),
  bstack1llllll11_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡖࡈࡐ࠭ऊ"),
  bstack1llllll11_opy_ (u"ࠬࡶࡲࡦࡸࡨࡲࡹࡉࡲࡰࡵࡶࡗ࡮ࡺࡥࡕࡴࡤࡧࡰ࡯࡮ࡨࠩऋ"),
  bstack1llllll11_opy_ (u"࠭ࡨࡪࡩ࡫ࡇࡴࡴࡴࡳࡣࡶࡸࠬऌ"),
  bstack1llllll11_opy_ (u"ࠧࡥࡧࡹ࡭ࡨ࡫ࡐࡳࡧࡩࡩࡷ࡫࡮ࡤࡧࡶࠫऍ"),
  bstack1llllll11_opy_ (u"ࠨࡧࡱࡥࡧࡲࡥࡔ࡫ࡰࠫऎ"),
  bstack1llllll11_opy_ (u"ࠩࡶ࡭ࡲࡕࡰࡵ࡫ࡲࡲࡸ࠭ए"),
  bstack1llllll11_opy_ (u"ࠪࡶࡪࡳ࡯ࡷࡧࡌࡓࡘࡇࡰࡱࡕࡨࡸࡹ࡯࡮ࡨࡵࡏࡳࡨࡧ࡬ࡪࡼࡤࡸ࡮ࡵ࡮ࠨऐ"),
  bstack1llllll11_opy_ (u"ࠫ࡭ࡵࡳࡵࡐࡤࡱࡪ࠭ऑ"),
  bstack1llllll11_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧऒ"),
  bstack1llllll11_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࠨओ"),
  bstack1llllll11_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡐࡤࡱࡪ࠭औ"),
  bstack1llllll11_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯࡙ࡩࡷࡹࡩࡰࡰࠪक"),
  bstack1llllll11_opy_ (u"ࠩࡳࡥ࡬࡫ࡌࡰࡣࡧࡗࡹࡸࡡࡵࡧࡪࡽࠬख"),
  bstack1llllll11_opy_ (u"ࠪࡴࡷࡵࡸࡺࠩग"),
  bstack1llllll11_opy_ (u"ࠫࡹ࡯࡭ࡦࡱࡸࡸࡸ࠭घ"),
  bstack1llllll11_opy_ (u"ࠬࡻ࡮ࡩࡣࡱࡨࡱ࡫ࡤࡑࡴࡲࡱࡵࡺࡂࡦࡪࡤࡺ࡮ࡵࡲࠨङ")
]
bstack111l111ll_opy_ = {
  bstack1llllll11_opy_ (u"࠭ࡶࠨच"): bstack1llllll11_opy_ (u"ࠧࡷࠩछ"),
  bstack1llllll11_opy_ (u"ࠨࡨࠪज"): bstack1llllll11_opy_ (u"ࠩࡩࠫझ"),
  bstack1llllll11_opy_ (u"ࠪࡪࡴࡸࡣࡦࠩञ"): bstack1llllll11_opy_ (u"ࠫ࡫ࡵࡲࡤࡧࠪट"),
  bstack1llllll11_opy_ (u"ࠬࡵ࡮࡭ࡻࡤࡹࡹࡵ࡭ࡢࡶࡨࠫठ"): bstack1llllll11_opy_ (u"࠭࡯࡯࡮ࡼࡅࡺࡺ࡯࡮ࡣࡷࡩࠬड"),
  bstack1llllll11_opy_ (u"ࠧࡧࡱࡵࡧࡪࡲ࡯ࡤࡣ࡯ࠫढ"): bstack1llllll11_opy_ (u"ࠨࡨࡲࡶࡨ࡫࡬ࡰࡥࡤࡰࠬण"),
  bstack1llllll11_opy_ (u"ࠩࡳࡶࡴࡾࡹࡩࡱࡶࡸࠬत"): bstack1llllll11_opy_ (u"ࠪࡴࡷࡵࡸࡺࡊࡲࡷࡹ࠭थ"),
  bstack1llllll11_opy_ (u"ࠫࡵࡸ࡯ࡹࡻࡳࡳࡷࡺࠧद"): bstack1llllll11_opy_ (u"ࠬࡶࡲࡰࡺࡼࡔࡴࡸࡴࠨध"),
  bstack1llllll11_opy_ (u"࠭ࡰࡳࡱࡻࡽࡺࡹࡥࡳࠩन"): bstack1llllll11_opy_ (u"ࠧࡱࡴࡲࡼࡾ࡛ࡳࡦࡴࠪऩ"),
  bstack1llllll11_opy_ (u"ࠨࡲࡵࡳࡽࡿࡰࡢࡵࡶࠫप"): bstack1llllll11_opy_ (u"ࠩࡳࡶࡴࡾࡹࡑࡣࡶࡷࠬफ"),
  bstack1llllll11_opy_ (u"ࠪࡰࡴࡩࡡ࡭ࡲࡵࡳࡽࡿࡨࡰࡵࡷࠫब"): bstack1llllll11_opy_ (u"ࠫࡱࡵࡣࡢ࡮ࡓࡶࡴࡾࡹࡉࡱࡶࡸࠬभ"),
  bstack1llllll11_opy_ (u"ࠬࡲ࡯ࡤࡣ࡯ࡴࡷࡵࡸࡺࡲࡲࡶࡹ࠭म"): bstack1llllll11_opy_ (u"࠭࡬ࡰࡥࡤࡰࡕࡸ࡯ࡹࡻࡓࡳࡷࡺࠧय"),
  bstack1llllll11_opy_ (u"ࠧ࡭ࡱࡦࡥࡱࡶࡲࡰࡺࡼࡹࡸ࡫ࡲࠨर"): bstack1llllll11_opy_ (u"ࠨ࠯࡯ࡳࡨࡧ࡬ࡑࡴࡲࡼࡾ࡛ࡳࡦࡴࠪऱ"),
  bstack1llllll11_opy_ (u"ࠩ࠰ࡰࡴࡩࡡ࡭ࡲࡵࡳࡽࡿࡵࡴࡧࡵࠫल"): bstack1llllll11_opy_ (u"ࠪ࠱ࡱࡵࡣࡢ࡮ࡓࡶࡴࡾࡹࡖࡵࡨࡶࠬळ"),
  bstack1llllll11_opy_ (u"ࠫࡱࡵࡣࡢ࡮ࡳࡶࡴࡾࡹࡱࡣࡶࡷࠬऴ"): bstack1llllll11_opy_ (u"ࠬ࠳࡬ࡰࡥࡤࡰࡕࡸ࡯ࡹࡻࡓࡥࡸࡹࠧव"),
  bstack1llllll11_opy_ (u"࠭࠭࡭ࡱࡦࡥࡱࡶࡲࡰࡺࡼࡴࡦࡹࡳࠨश"): bstack1llllll11_opy_ (u"ࠧ࠮࡮ࡲࡧࡦࡲࡐࡳࡱࡻࡽࡕࡧࡳࡴࠩष"),
  bstack1llllll11_opy_ (u"ࠨࡤ࡬ࡲࡦࡸࡹࡱࡣࡷ࡬ࠬस"): bstack1llllll11_opy_ (u"ࠩࡥ࡭ࡳࡧࡲࡺࡲࡤࡸ࡭࠭ह"),
  bstack1llllll11_opy_ (u"ࠪࡴࡦࡩࡦࡪ࡮ࡨࠫऺ"): bstack1llllll11_opy_ (u"ࠫ࠲ࡶࡡࡤ࠯ࡩ࡭ࡱ࡫ࠧऻ"),
  bstack1llllll11_opy_ (u"ࠬࡶࡡࡤ࠯ࡩ࡭ࡱ࡫़ࠧ"): bstack1llllll11_opy_ (u"࠭࠭ࡱࡣࡦ࠱࡫࡯࡬ࡦࠩऽ"),
  bstack1llllll11_opy_ (u"ࠧ࠮ࡲࡤࡧ࠲࡬ࡩ࡭ࡧࠪा"): bstack1llllll11_opy_ (u"ࠨ࠯ࡳࡥࡨ࠳ࡦࡪ࡮ࡨࠫि"),
  bstack1llllll11_opy_ (u"ࠩ࡯ࡳ࡬࡬ࡩ࡭ࡧࠪी"): bstack1llllll11_opy_ (u"ࠪࡰࡴ࡭ࡦࡪ࡮ࡨࠫु"),
  bstack1llllll11_opy_ (u"ࠫࡱࡵࡣࡢ࡮࡬ࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ू"): bstack1llllll11_opy_ (u"ࠬࡲ࡯ࡤࡣ࡯ࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧृ"),
}
bstack1111l111_opy_ = bstack1llllll11_opy_ (u"࠭ࡨࡵࡶࡳࡷ࠿࠵࠯ࡩࡷࡥ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡧࡴࡳ࠯ࡸࡦ࠲࡬ࡺࡨࠧॄ")
bstack1ll111ll_opy_ = bstack1llllll11_opy_ (u"ࠧࡩࡶࡷࡴ࠿࠵࠯ࡩࡷࡥ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡧࡴࡳ࠺࠹࠲࠲ࡻࡩ࠵ࡨࡶࡤࠪॅ")
bstack1111l_opy_ = bstack1llllll11_opy_ (u"ࠨࡪࡷࡸࡵࡹ࠺࠰࠱࡫ࡹࡧ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮࠱ࡱࡩࡽࡺ࡟ࡩࡷࡥࡷࠬॆ")
bstack11ll1llll_opy_ = {
  bstack1llllll11_opy_ (u"ࠩࡦࡶ࡮ࡺࡩࡤࡣ࡯ࠫे"): 50,
  bstack1llllll11_opy_ (u"ࠪࡩࡷࡸ࡯ࡳࠩै"): 40,
  bstack1llllll11_opy_ (u"ࠫࡼࡧࡲ࡯࡫ࡱ࡫ࠬॉ"): 30,
  bstack1llllll11_opy_ (u"ࠬ࡯࡮ࡧࡱࠪॊ"): 20,
  bstack1llllll11_opy_ (u"࠭ࡤࡦࡤࡸ࡫ࠬो"): 10
}
bstack111llll1_opy_ = bstack11ll1llll_opy_[bstack1llllll11_opy_ (u"ࠧࡪࡰࡩࡳࠬौ")]
bstack11ll11l1_opy_ = bstack1llllll11_opy_ (u"ࠨࡲࡼࡸ࡭ࡵ࡮࠮ࡲࡼࡸ࡭ࡵ࡮ࡢࡩࡨࡲࡹ࠵्ࠧ")
bstack111lll11_opy_ = bstack1llllll11_opy_ (u"ࠩࡵࡳࡧࡵࡴ࠮ࡲࡼࡸ࡭ࡵ࡮ࡢࡩࡨࡲࡹ࠵ࠧॎ")
bstack1ll1ll111_opy_ = bstack1llllll11_opy_ (u"ࠪࡦࡪ࡮ࡡࡷࡧ࠰ࡴࡾࡺࡨࡰࡰࡤ࡫ࡪࡴࡴ࠰ࠩॏ")
bstack111ll11_opy_ = bstack1llllll11_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷ࠱ࡵࡿࡴࡩࡱࡱࡥ࡬࡫࡮ࡵ࠱ࠪॐ")
bstack11lll1111_opy_ = [bstack1llllll11_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡚࡙ࡅࡓࡐࡄࡑࡊ࠭॑"), bstack1llllll11_opy_ (u"࡙࠭ࡐࡗࡕࡣ࡚࡙ࡅࡓࡐࡄࡑࡊ॒࠭")]
bstack111lll11l_opy_ = [bstack1llllll11_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡁࡄࡅࡈࡗࡘࡥࡋࡆ࡛ࠪ॓"), bstack1llllll11_opy_ (u"ࠨ࡛ࡒ࡙ࡗࡥࡁࡄࡅࡈࡗࡘࡥࡋࡆ࡛ࠪ॔")]
bstack1lllll111_opy_ = [
  bstack1llllll11_opy_ (u"ࠩࡤࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࡔࡡ࡮ࡧࠪॕ"),
  bstack1llllll11_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱ࡛࡫ࡲࡴ࡫ࡲࡲࠬॖ"),
  bstack1llllll11_opy_ (u"ࠫࡩ࡫ࡶࡪࡥࡨࡒࡦࡳࡥࠨॗ"),
  bstack1llllll11_opy_ (u"ࠬࡴࡥࡸࡅࡲࡱࡲࡧ࡮ࡥࡖ࡬ࡱࡪࡵࡵࡵࠩक़"),
  bstack1llllll11_opy_ (u"࠭ࡡࡱࡲࠪख़"),
  bstack1llllll11_opy_ (u"ࠧࡶࡦ࡬ࡨࠬग़"),
  bstack1llllll11_opy_ (u"ࠨ࡮ࡤࡲ࡬ࡻࡡࡨࡧࠪज़"),
  bstack1llllll11_opy_ (u"ࠩ࡯ࡳࡨࡧ࡬ࡦࠩड़"),
  bstack1llllll11_opy_ (u"ࠪࡳࡷ࡯ࡥ࡯ࡶࡤࡸ࡮ࡵ࡮ࠨढ़"),
  bstack1llllll11_opy_ (u"ࠫࡦࡻࡴࡰ࡙ࡨࡦࡻ࡯ࡥࡸࠩफ़"),
  bstack1llllll11_opy_ (u"ࠬࡴ࡯ࡓࡧࡶࡩࡹ࠭य़"), bstack1llllll11_opy_ (u"࠭ࡦࡶ࡮࡯ࡖࡪࡹࡥࡵࠩॠ"),
  bstack1llllll11_opy_ (u"ࠧࡤ࡮ࡨࡥࡷ࡙ࡹࡴࡶࡨࡱࡋ࡯࡬ࡦࡵࠪॡ"),
  bstack1llllll11_opy_ (u"ࠨࡧࡹࡩࡳࡺࡔࡪ࡯࡬ࡲ࡬ࡹࠧॢ"),
  bstack1llllll11_opy_ (u"ࠩࡨࡲࡦࡨ࡬ࡦࡒࡨࡶ࡫ࡵࡲ࡮ࡣࡱࡧࡪࡒ࡯ࡨࡩ࡬ࡲ࡬࠭ॣ"),
  bstack1llllll11_opy_ (u"ࠪࡳࡹ࡮ࡥࡳࡃࡳࡴࡸ࠭।"),
  bstack1llllll11_opy_ (u"ࠫࡵࡸࡩ࡯ࡶࡓࡥ࡬࡫ࡓࡰࡷࡵࡧࡪࡕ࡮ࡇ࡫ࡱࡨࡋࡧࡩ࡭ࡷࡵࡩࠬ॥"),
  bstack1llllll11_opy_ (u"ࠬࡧࡰࡱࡃࡦࡸ࡮ࡼࡩࡵࡻࠪ०"), bstack1llllll11_opy_ (u"࠭ࡡࡱࡲࡓࡥࡨࡱࡡࡨࡧࠪ१"), bstack1llllll11_opy_ (u"ࠧࡢࡲࡳ࡛ࡦ࡯ࡴࡂࡥࡷ࡭ࡻ࡯ࡴࡺࠩ२"), bstack1llllll11_opy_ (u"ࠨࡣࡳࡴ࡜ࡧࡩࡵࡒࡤࡧࡰࡧࡧࡦࠩ३"), bstack1llllll11_opy_ (u"ࠩࡤࡴࡵ࡝ࡡࡪࡶࡇࡹࡷࡧࡴࡪࡱࡱࠫ४"),
  bstack1llllll11_opy_ (u"ࠪࡨࡪࡼࡩࡤࡧࡕࡩࡦࡪࡹࡕ࡫ࡰࡩࡴࡻࡴࠨ५"),
  bstack1llllll11_opy_ (u"ࠫࡦࡲ࡬ࡰࡹࡗࡩࡸࡺࡐࡢࡥ࡮ࡥ࡬࡫ࡳࠨ६"),
  bstack1llllll11_opy_ (u"ࠬࡧ࡮ࡥࡴࡲ࡭ࡩࡉ࡯ࡷࡧࡵࡥ࡬࡫ࠧ७"), bstack1llllll11_opy_ (u"࠭ࡡ࡯ࡦࡵࡳ࡮ࡪࡃࡰࡸࡨࡶࡦ࡭ࡥࡆࡰࡧࡍࡳࡺࡥ࡯ࡶࠪ८"),
  bstack1llllll11_opy_ (u"ࠧࡢࡰࡧࡶࡴ࡯ࡤࡅࡧࡹ࡭ࡨ࡫ࡒࡦࡣࡧࡽ࡙࡯࡭ࡦࡱࡸࡸࠬ९"),
  bstack1llllll11_opy_ (u"ࠨࡣࡧࡦࡕࡵࡲࡵࠩ॰"),
  bstack1llllll11_opy_ (u"ࠩࡤࡲࡩࡸ࡯ࡪࡦࡇࡩࡻ࡯ࡣࡦࡕࡲࡧࡰ࡫ࡴࠨॱ"),
  bstack1llllll11_opy_ (u"ࠪࡥࡳࡪࡲࡰ࡫ࡧࡍࡳࡹࡴࡢ࡮࡯ࡘ࡮ࡳࡥࡰࡷࡷࠫॲ"),
  bstack1llllll11_opy_ (u"ࠫࡦࡴࡤࡳࡱ࡬ࡨࡎࡴࡳࡵࡣ࡯ࡰࡕࡧࡴࡩࠩॳ"),
  bstack1llllll11_opy_ (u"ࠬࡧࡶࡥࠩॴ"), bstack1llllll11_opy_ (u"࠭ࡡࡷࡦࡏࡥࡺࡴࡣࡩࡖ࡬ࡱࡪࡵࡵࡵࠩॵ"), bstack1llllll11_opy_ (u"ࠧࡢࡸࡧࡖࡪࡧࡤࡺࡖ࡬ࡱࡪࡵࡵࡵࠩॶ"), bstack1llllll11_opy_ (u"ࠨࡣࡹࡨࡆࡸࡧࡴࠩॷ"),
  bstack1llllll11_opy_ (u"ࠩࡸࡷࡪࡑࡥࡺࡵࡷࡳࡷ࡫ࠧॸ"), bstack1llllll11_opy_ (u"ࠪ࡯ࡪࡿࡳࡵࡱࡵࡩࡕࡧࡴࡩࠩॹ"), bstack1llllll11_opy_ (u"ࠫࡰ࡫ࡹࡴࡶࡲࡶࡪࡖࡡࡴࡵࡺࡳࡷࡪࠧॺ"),
  bstack1llllll11_opy_ (u"ࠬࡱࡥࡺࡃ࡯࡭ࡦࡹࠧॻ"), bstack1llllll11_opy_ (u"࠭࡫ࡦࡻࡓࡥࡸࡹࡷࡰࡴࡧࠫॼ"),
  bstack1llllll11_opy_ (u"ࠧࡤࡪࡵࡳࡲ࡫ࡤࡳ࡫ࡹࡩࡷࡋࡸࡦࡥࡸࡸࡦࡨ࡬ࡦࠩॽ"), bstack1llllll11_opy_ (u"ࠨࡥ࡫ࡶࡴࡳࡥࡥࡴ࡬ࡺࡪࡸࡁࡳࡩࡶࠫॾ"), bstack1llllll11_opy_ (u"ࠩࡦ࡬ࡷࡵ࡭ࡦࡦࡵ࡭ࡻ࡫ࡲࡆࡺࡨࡧࡺࡺࡡࡣ࡮ࡨࡈ࡮ࡸࠧॿ"), bstack1llllll11_opy_ (u"ࠪࡧ࡭ࡸ࡯࡮ࡧࡧࡶ࡮ࡼࡥࡳࡅ࡫ࡶࡴࡳࡥࡎࡣࡳࡴ࡮ࡴࡧࡇ࡫࡯ࡩࠬঀ"), bstack1llllll11_opy_ (u"ࠫࡨ࡮ࡲࡰ࡯ࡨࡨࡷ࡯ࡶࡦࡴࡘࡷࡪ࡙ࡹࡴࡶࡨࡱࡊࡾࡥࡤࡷࡷࡥࡧࡲࡥࠨঁ"),
  bstack1llllll11_opy_ (u"ࠬࡩࡨࡳࡱࡰࡩࡩࡸࡩࡷࡧࡵࡔࡴࡸࡴࠨং"), bstack1llllll11_opy_ (u"࠭ࡣࡩࡴࡲࡱࡪࡪࡲࡪࡸࡨࡶࡕࡵࡲࡵࡵࠪঃ"),
  bstack1llllll11_opy_ (u"ࠧࡤࡪࡵࡳࡲ࡫ࡤࡳ࡫ࡹࡩࡷࡊࡩࡴࡣࡥࡰࡪࡈࡵࡪ࡮ࡧࡇ࡭࡫ࡣ࡬ࠩ঄"),
  bstack1llllll11_opy_ (u"ࠨࡣࡸࡸࡴ࡝ࡥࡣࡸ࡬ࡩࡼ࡚ࡩ࡮ࡧࡲࡹࡹ࠭অ"),
  bstack1llllll11_opy_ (u"ࠩ࡬ࡲࡹ࡫࡮ࡵࡃࡦࡸ࡮ࡵ࡮ࠨআ"), bstack1llllll11_opy_ (u"ࠪ࡭ࡳࡺࡥ࡯ࡶࡆࡥࡹ࡫ࡧࡰࡴࡼࠫই"), bstack1llllll11_opy_ (u"ࠫ࡮ࡴࡴࡦࡰࡷࡊࡱࡧࡧࡴࠩঈ"), bstack1llllll11_opy_ (u"ࠬࡵࡰࡵ࡫ࡲࡲࡦࡲࡉ࡯ࡶࡨࡲࡹࡇࡲࡨࡷࡰࡩࡳࡺࡳࠨউ"),
  bstack1llllll11_opy_ (u"࠭ࡤࡰࡰࡷࡗࡹࡵࡰࡂࡲࡳࡓࡳࡘࡥࡴࡧࡷࠫঊ"),
  bstack1llllll11_opy_ (u"ࠧࡶࡰ࡬ࡧࡴࡪࡥࡌࡧࡼࡦࡴࡧࡲࡥࠩঋ"), bstack1llllll11_opy_ (u"ࠨࡴࡨࡷࡪࡺࡋࡦࡻࡥࡳࡦࡸࡤࠨঌ"),
  bstack1llllll11_opy_ (u"ࠩࡱࡳࡘ࡯ࡧ࡯ࠩ঍"),
  bstack1llllll11_opy_ (u"ࠪ࡭࡬ࡴ࡯ࡳࡧࡘࡲ࡮ࡳࡰࡰࡴࡷࡥࡳࡺࡖࡪࡧࡺࡷࠬ঎"),
  bstack1llllll11_opy_ (u"ࠫࡩ࡯ࡳࡢࡤ࡯ࡩࡆࡴࡤࡳࡱ࡬ࡨ࡜ࡧࡴࡤࡪࡨࡶࡸ࠭এ"),
  bstack1llllll11_opy_ (u"ࠬࡩࡨࡳࡱࡰࡩࡔࡶࡴࡪࡱࡱࡷࠬঐ"),
  bstack1llllll11_opy_ (u"࠭ࡲࡦࡥࡵࡩࡦࡺࡥࡄࡪࡵࡳࡲ࡫ࡄࡳ࡫ࡹࡩࡷ࡙ࡥࡴࡵ࡬ࡳࡳࡹࠧ঑"),
  bstack1llllll11_opy_ (u"ࠧ࡯ࡣࡷ࡭ࡻ࡫ࡗࡦࡤࡖࡧࡷ࡫ࡥ࡯ࡵ࡫ࡳࡹ࠭঒"),
  bstack1llllll11_opy_ (u"ࠨࡣࡱࡨࡷࡵࡩࡥࡕࡦࡶࡪ࡫࡮ࡴࡪࡲࡸࡕࡧࡴࡩࠩও"),
  bstack1llllll11_opy_ (u"ࠩࡱࡩࡹࡽ࡯ࡳ࡭ࡖࡴࡪ࡫ࡤࠨঔ"),
  bstack1llllll11_opy_ (u"ࠪ࡫ࡵࡹࡅ࡯ࡣࡥࡰࡪࡪࠧক"),
  bstack1llllll11_opy_ (u"ࠫ࡮ࡹࡈࡦࡣࡧࡰࡪࡹࡳࠨখ"),
  bstack1llllll11_opy_ (u"ࠬࡧࡤࡣࡇࡻࡩࡨ࡚ࡩ࡮ࡧࡲࡹࡹ࠭গ"),
  bstack1llllll11_opy_ (u"࠭࡬ࡰࡥࡤࡰࡪ࡙ࡣࡳ࡫ࡳࡸࠬঘ"),
  bstack1llllll11_opy_ (u"ࠧࡴ࡭࡬ࡴࡉ࡫ࡶࡪࡥࡨࡍࡳ࡯ࡴࡪࡣ࡯࡭ࡿࡧࡴࡪࡱࡱࠫঙ"),
  bstack1llllll11_opy_ (u"ࠨࡣࡸࡸࡴࡍࡲࡢࡰࡷࡔࡪࡸ࡭ࡪࡵࡶ࡭ࡴࡴࡳࠨচ"),
  bstack1llllll11_opy_ (u"ࠩࡤࡲࡩࡸ࡯ࡪࡦࡑࡥࡹࡻࡲࡢ࡮ࡒࡶ࡮࡫࡮ࡵࡣࡷ࡭ࡴࡴࠧছ"),
  bstack1llllll11_opy_ (u"ࠪࡷࡾࡹࡴࡦ࡯ࡓࡳࡷࡺࠧজ"),
  bstack1llllll11_opy_ (u"ࠫࡷ࡫࡭ࡰࡶࡨࡅࡩࡨࡈࡰࡵࡷࠫঝ"),
  bstack1llllll11_opy_ (u"ࠬࡹ࡫ࡪࡲࡘࡲࡱࡵࡣ࡬ࠩঞ"), bstack1llllll11_opy_ (u"࠭ࡵ࡯࡮ࡲࡧࡰ࡚ࡹࡱࡧࠪট"), bstack1llllll11_opy_ (u"ࠧࡶࡰ࡯ࡳࡨࡱࡋࡦࡻࠪঠ"),
  bstack1llllll11_opy_ (u"ࠨࡣࡸࡸࡴࡒࡡࡶࡰࡦ࡬ࠬড"),
  bstack1llllll11_opy_ (u"ࠩࡶ࡯࡮ࡶࡌࡰࡩࡦࡥࡹࡉࡡࡱࡶࡸࡶࡪ࠭ঢ"),
  bstack1llllll11_opy_ (u"ࠪࡹࡳ࡯࡮ࡴࡶࡤࡰࡱࡕࡴࡩࡧࡵࡔࡦࡩ࡫ࡢࡩࡨࡷࠬণ"),
  bstack1llllll11_opy_ (u"ࠫࡩ࡯ࡳࡢࡤ࡯ࡩ࡜࡯࡮ࡥࡱࡺࡅࡳ࡯࡭ࡢࡶ࡬ࡳࡳ࠭ত"),
  bstack1llllll11_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡘࡴࡵ࡬ࡴࡘࡨࡶࡸ࡯࡯࡯ࠩথ"),
  bstack1llllll11_opy_ (u"࠭ࡥ࡯ࡨࡲࡶࡨ࡫ࡁࡱࡲࡌࡲࡸࡺࡡ࡭࡮ࠪদ"),
  bstack1llllll11_opy_ (u"ࠧࡦࡰࡶࡹࡷ࡫ࡗࡦࡤࡹ࡭ࡪࡽࡳࡉࡣࡹࡩࡕࡧࡧࡦࡵࠪধ"), bstack1llllll11_opy_ (u"ࠨࡹࡨࡦࡻ࡯ࡥࡸࡆࡨࡺࡹࡵ࡯࡭ࡵࡓࡳࡷࡺࠧন"), bstack1llllll11_opy_ (u"ࠩࡨࡲࡦࡨ࡬ࡦ࡙ࡨࡦࡻ࡯ࡥࡸࡆࡨࡸࡦ࡯࡬ࡴࡅࡲࡰࡱ࡫ࡣࡵ࡫ࡲࡲࠬ঩"),
  bstack1llllll11_opy_ (u"ࠪࡶࡪࡳ࡯ࡵࡧࡄࡴࡵࡹࡃࡢࡥ࡫ࡩࡑ࡯࡭ࡪࡶࠪপ"),
  bstack1llllll11_opy_ (u"ࠫࡨࡧ࡬ࡦࡰࡧࡥࡷࡌ࡯ࡳ࡯ࡤࡸࠬফ"),
  bstack1llllll11_opy_ (u"ࠬࡨࡵ࡯ࡦ࡯ࡩࡎࡪࠧব"),
  bstack1llllll11_opy_ (u"࠭࡬ࡢࡷࡱࡧ࡭࡚ࡩ࡮ࡧࡲࡹࡹ࠭ভ"),
  bstack1llllll11_opy_ (u"ࠧ࡭ࡱࡦࡥࡹ࡯࡯࡯ࡕࡨࡶࡻ࡯ࡣࡦࡵࡈࡲࡦࡨ࡬ࡦࡦࠪম"), bstack1llllll11_opy_ (u"ࠨ࡮ࡲࡧࡦࡺࡩࡰࡰࡖࡩࡷࡼࡩࡤࡧࡶࡅࡺࡺࡨࡰࡴ࡬ࡾࡪࡪࠧয"),
  bstack1llllll11_opy_ (u"ࠩࡤࡹࡹࡵࡁࡤࡥࡨࡴࡹࡇ࡬ࡦࡴࡷࡷࠬর"), bstack1llllll11_opy_ (u"ࠪࡥࡺࡺ࡯ࡅ࡫ࡶࡱ࡮ࡹࡳࡂ࡮ࡨࡶࡹࡹࠧ঱"),
  bstack1llllll11_opy_ (u"ࠫࡳࡧࡴࡪࡸࡨࡍࡳࡹࡴࡳࡷࡰࡩࡳࡺࡳࡍ࡫ࡥࠫল"),
  bstack1llllll11_opy_ (u"ࠬࡴࡡࡵ࡫ࡹࡩ࡜࡫ࡢࡕࡣࡳࠫ঳"),
  bstack1llllll11_opy_ (u"࠭ࡳࡢࡨࡤࡶ࡮ࡏ࡮ࡪࡶ࡬ࡥࡱ࡛ࡲ࡭ࠩ঴"), bstack1llllll11_opy_ (u"ࠧࡴࡣࡩࡥࡷ࡯ࡁ࡭࡮ࡲࡻࡕࡵࡰࡶࡲࡶࠫ঵"), bstack1llllll11_opy_ (u"ࠨࡵࡤࡪࡦࡸࡩࡊࡩࡱࡳࡷ࡫ࡆࡳࡣࡸࡨ࡜ࡧࡲ࡯࡫ࡱ࡫ࠬশ"), bstack1llllll11_opy_ (u"ࠩࡶࡥ࡫ࡧࡲࡪࡑࡳࡩࡳࡒࡩ࡯࡭ࡶࡍࡳࡈࡡࡤ࡭ࡪࡶࡴࡻ࡮ࡥࠩষ"),
  bstack1llllll11_opy_ (u"ࠪ࡯ࡪ࡫ࡰࡌࡧࡼࡇ࡭ࡧࡩ࡯ࡵࠪস"),
  bstack1llllll11_opy_ (u"ࠫࡱࡵࡣࡢ࡮࡬ࡾࡦࡨ࡬ࡦࡕࡷࡶ࡮ࡴࡧࡴࡆ࡬ࡶࠬহ"),
  bstack1llllll11_opy_ (u"ࠬࡶࡲࡰࡥࡨࡷࡸࡇࡲࡨࡷࡰࡩࡳࡺࡳࠨ঺"),
  bstack1llllll11_opy_ (u"࠭ࡩ࡯ࡶࡨࡶࡐ࡫ࡹࡅࡧ࡯ࡥࡾ࠭঻"),
  bstack1llllll11_opy_ (u"ࠧࡴࡪࡲࡻࡎࡕࡓࡍࡱࡪ়ࠫ"),
  bstack1llllll11_opy_ (u"ࠨࡵࡨࡲࡩࡑࡥࡺࡕࡷࡶࡦࡺࡥࡨࡻࠪঽ"),
  bstack1llllll11_opy_ (u"ࠩࡺࡩࡧࡱࡩࡵࡔࡨࡷࡵࡵ࡮ࡴࡧࡗ࡭ࡲ࡫࡯ࡶࡶࠪা"), bstack1llllll11_opy_ (u"ࠪࡷࡨࡸࡥࡦࡰࡶ࡬ࡴࡺࡗࡢ࡫ࡷࡘ࡮ࡳࡥࡰࡷࡷࠫি"),
  bstack1llllll11_opy_ (u"ࠫࡷ࡫࡭ࡰࡶࡨࡈࡪࡨࡵࡨࡒࡵࡳࡽࡿࠧী"),
  bstack1llllll11_opy_ (u"ࠬ࡫࡮ࡢࡤ࡯ࡩࡆࡹࡹ࡯ࡥࡈࡼࡪࡩࡵࡵࡧࡉࡶࡴࡳࡈࡵࡶࡳࡷࠬু"),
  bstack1llllll11_opy_ (u"࠭ࡳ࡬࡫ࡳࡐࡴ࡭ࡃࡢࡲࡷࡹࡷ࡫ࠧূ"),
  bstack1llllll11_opy_ (u"ࠧࡸࡧࡥ࡯࡮ࡺࡄࡦࡤࡸ࡫ࡕࡸ࡯ࡹࡻࡓࡳࡷࡺࠧৃ"),
  bstack1llllll11_opy_ (u"ࠨࡨࡸࡰࡱࡉ࡯࡯ࡶࡨࡼࡹࡒࡩࡴࡶࠪৄ"),
  bstack1llllll11_opy_ (u"ࠩࡺࡥ࡮ࡺࡆࡰࡴࡄࡴࡵ࡙ࡣࡳ࡫ࡳࡸࠬ৅"),
  bstack1llllll11_opy_ (u"ࠪࡻࡪࡨࡶࡪࡧࡺࡇࡴࡴ࡮ࡦࡥࡷࡖࡪࡺࡲࡪࡧࡶࠫ৆"),
  bstack1llllll11_opy_ (u"ࠫࡦࡶࡰࡏࡣࡰࡩࠬে"),
  bstack1llllll11_opy_ (u"ࠬࡩࡵࡴࡶࡲࡱࡘ࡙ࡌࡄࡧࡵࡸࠬৈ"),
  bstack1llllll11_opy_ (u"࠭ࡴࡢࡲ࡚࡭ࡹ࡮ࡓࡩࡱࡵࡸࡕࡸࡥࡴࡵࡇࡹࡷࡧࡴࡪࡱࡱࠫ৉"),
  bstack1llllll11_opy_ (u"ࠧࡴࡥࡤࡰࡪࡌࡡࡤࡶࡲࡶࠬ৊"),
  bstack1llllll11_opy_ (u"ࠨࡹࡧࡥࡑࡵࡣࡢ࡮ࡓࡳࡷࡺࠧো"),
  bstack1llllll11_opy_ (u"ࠩࡶ࡬ࡴࡽࡘࡤࡱࡧࡩࡑࡵࡧࠨৌ"),
  bstack1llllll11_opy_ (u"ࠪ࡭ࡴࡹࡉ࡯ࡵࡷࡥࡱࡲࡐࡢࡷࡶࡩ্ࠬ"),
  bstack1llllll11_opy_ (u"ࠫࡽࡩ࡯ࡥࡧࡆࡳࡳ࡬ࡩࡨࡈ࡬ࡰࡪ࠭ৎ"),
  bstack1llllll11_opy_ (u"ࠬࡱࡥࡺࡥ࡫ࡥ࡮ࡴࡐࡢࡵࡶࡻࡴࡸࡤࠨ৏"),
  bstack1llllll11_opy_ (u"࠭ࡵࡴࡧࡓࡶࡪࡨࡵࡪ࡮ࡷ࡛ࡉࡇࠧ৐"),
  bstack1llllll11_opy_ (u"ࠧࡱࡴࡨࡺࡪࡴࡴࡘࡆࡄࡅࡹࡺࡡࡤࡪࡰࡩࡳࡺࡳࠨ৑"),
  bstack1llllll11_opy_ (u"ࠨࡹࡨࡦࡉࡸࡩࡷࡧࡵࡅ࡬࡫࡮ࡵࡗࡵࡰࠬ৒"),
  bstack1llllll11_opy_ (u"ࠩ࡮ࡩࡾࡩࡨࡢ࡫ࡱࡔࡦࡺࡨࠨ৓"),
  bstack1llllll11_opy_ (u"ࠪࡹࡸ࡫ࡎࡦࡹ࡚ࡈࡆ࠭৔"),
  bstack1llllll11_opy_ (u"ࠫࡼࡪࡡࡍࡣࡸࡲࡨ࡮ࡔࡪ࡯ࡨࡳࡺࡺࠧ৕"), bstack1llllll11_opy_ (u"ࠬࡽࡤࡢࡅࡲࡲࡳ࡫ࡣࡵ࡫ࡲࡲ࡙࡯࡭ࡦࡱࡸࡸࠬ৖"),
  bstack1llllll11_opy_ (u"࠭ࡸࡤࡱࡧࡩࡔࡸࡧࡊࡦࠪৗ"), bstack1llllll11_opy_ (u"ࠧࡹࡥࡲࡨࡪ࡙ࡩࡨࡰ࡬ࡲ࡬ࡏࡤࠨ৘"),
  bstack1llllll11_opy_ (u"ࠨࡷࡳࡨࡦࡺࡥࡥ࡙ࡇࡅࡇࡻ࡮ࡥ࡮ࡨࡍࡩ࠭৙"),
  bstack1llllll11_opy_ (u"ࠩࡵࡩࡸ࡫ࡴࡐࡰࡖࡩࡸࡹࡩࡰࡰࡖࡸࡦࡸࡴࡐࡰ࡯ࡽࠬ৚"),
  bstack1llllll11_opy_ (u"ࠪࡧࡴࡳ࡭ࡢࡰࡧࡘ࡮ࡳࡥࡰࡷࡷࡷࠬ৛"),
  bstack1llllll11_opy_ (u"ࠫࡼࡪࡡࡔࡶࡤࡶࡹࡻࡰࡓࡧࡷࡶ࡮࡫ࡳࠨড়"), bstack1llllll11_opy_ (u"ࠬࡽࡤࡢࡕࡷࡥࡷࡺࡵࡱࡔࡨࡸࡷࡿࡉ࡯ࡶࡨࡶࡻࡧ࡬ࠨঢ়"),
  bstack1llllll11_opy_ (u"࠭ࡣࡰࡰࡱࡩࡨࡺࡈࡢࡴࡧࡻࡦࡸࡥࡌࡧࡼࡦࡴࡧࡲࡥࠩ৞"),
  bstack1llllll11_opy_ (u"ࠧ࡮ࡣࡻࡘࡾࡶࡩ࡯ࡩࡉࡶࡪࡷࡵࡦࡰࡦࡽࠬয়"),
  bstack1llllll11_opy_ (u"ࠨࡵ࡬ࡱࡵࡲࡥࡊࡵ࡙࡭ࡸ࡯ࡢ࡭ࡧࡆ࡬ࡪࡩ࡫ࠨৠ"),
  bstack1llllll11_opy_ (u"ࠩࡸࡷࡪࡉࡡࡳࡶ࡫ࡥ࡬࡫ࡓࡴ࡮ࠪৡ"),
  bstack1llllll11_opy_ (u"ࠪࡷ࡭ࡵࡵ࡭ࡦࡘࡷࡪ࡙ࡩ࡯ࡩ࡯ࡩࡹࡵ࡮ࡕࡧࡶࡸࡒࡧ࡮ࡢࡩࡨࡶࠬৢ"),
  bstack1llllll11_opy_ (u"ࠫࡸࡺࡡࡳࡶࡌ࡛ࡉࡖࠧৣ"),
  bstack1llllll11_opy_ (u"ࠬࡧ࡬࡭ࡱࡺࡘࡴࡻࡣࡩࡋࡧࡉࡳࡸ࡯࡭࡮ࠪ৤"),
  bstack1llllll11_opy_ (u"࠭ࡩࡨࡰࡲࡶࡪࡎࡩࡥࡦࡨࡲࡆࡶࡩࡑࡱ࡯࡭ࡨࡿࡅࡳࡴࡲࡶࠬ৥"),
  bstack1llllll11_opy_ (u"ࠧ࡮ࡱࡦ࡯ࡑࡵࡣࡢࡶ࡬ࡳࡳࡇࡰࡱࠩ০"),
  bstack1llllll11_opy_ (u"ࠨ࡮ࡲ࡫ࡨࡧࡴࡇࡱࡵࡱࡦࡺࠧ১"), bstack1llllll11_opy_ (u"ࠩ࡯ࡳ࡬ࡩࡡࡵࡈ࡬ࡰࡹ࡫ࡲࡔࡲࡨࡧࡸ࠭২"),
  bstack1llllll11_opy_ (u"ࠪࡥࡱࡲ࡯ࡸࡆࡨࡰࡦࡿࡁࡥࡤࠪ৩")
]
bstack1l111111_opy_ = bstack1llllll11_opy_ (u"ࠫ࡭ࡺࡴࡱࡵ࠽࠳࠴ࡧࡰࡪ࠯ࡦࡰࡴࡻࡤ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡱࡰ࠳ࡦࡶࡰ࠮ࡣࡸࡸࡴࡳࡡࡵࡧ࠲ࡹࡵࡲ࡯ࡢࡦࠪ৪")
bstack1ll1ll1l_opy_ = [bstack1llllll11_opy_ (u"ࠬ࠴ࡡࡱ࡭ࠪ৫"), bstack1llllll11_opy_ (u"࠭࠮ࡢࡣࡥࠫ৬"), bstack1llllll11_opy_ (u"ࠧ࠯࡫ࡳࡥࠬ৭")]
bstack1l1111ll_opy_ = [bstack1llllll11_opy_ (u"ࠨ࡫ࡧࠫ৮"), bstack1llllll11_opy_ (u"ࠩࡳࡥࡹ࡮ࠧ৯"), bstack1llllll11_opy_ (u"ࠪࡧࡺࡹࡴࡰ࡯ࡢ࡭ࡩ࠭ৰ"), bstack1llllll11_opy_ (u"ࠫࡸ࡮ࡡࡳࡧࡤࡦࡱ࡫࡟ࡪࡦࠪৱ")]
bstack11lll1l1l_opy_ = {
  bstack1llllll11_opy_ (u"ࠬࡩࡨࡳࡱࡰࡩࡔࡶࡴࡪࡱࡱࡷࠬ৲"): bstack1llllll11_opy_ (u"࠭ࡧࡰࡱࡪ࠾ࡨ࡮ࡲࡰ࡯ࡨࡓࡵࡺࡩࡰࡰࡶࠫ৳"),
  bstack1llllll11_opy_ (u"ࠧࡧ࡫ࡵࡩ࡫ࡵࡸࡐࡲࡷ࡭ࡴࡴࡳࠨ৴"): bstack1llllll11_opy_ (u"ࠨ࡯ࡲࡾ࠿࡬ࡩࡳࡧࡩࡳࡽࡕࡰࡵ࡫ࡲࡲࡸ࠭৵"),
  bstack1llllll11_opy_ (u"ࠩࡨࡨ࡬࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧ৶"): bstack1llllll11_opy_ (u"ࠪࡱࡸࡀࡥࡥࡩࡨࡓࡵࡺࡩࡰࡰࡶࠫ৷"),
  bstack1llllll11_opy_ (u"ࠫ࡮࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧ৸"): bstack1llllll11_opy_ (u"ࠬࡹࡥ࠻࡫ࡨࡓࡵࡺࡩࡰࡰࡶࠫ৹"),
  bstack1llllll11_opy_ (u"࠭ࡳࡢࡨࡤࡶ࡮ࡕࡰࡵ࡫ࡲࡲࡸ࠭৺"): bstack1llllll11_opy_ (u"ࠧࡴࡣࡩࡥࡷ࡯࠮ࡰࡲࡷ࡭ࡴࡴࡳࠨ৻")
}
bstack11l1l11l_opy_ = [
  bstack1llllll11_opy_ (u"ࠨࡩࡲࡳ࡬ࡀࡣࡩࡴࡲࡱࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭ৼ"),
  bstack1llllll11_opy_ (u"ࠩࡰࡳࡿࡀࡦࡪࡴࡨࡪࡴࡾࡏࡱࡶ࡬ࡳࡳࡹࠧ৽"),
  bstack1llllll11_opy_ (u"ࠪࡱࡸࡀࡥࡥࡩࡨࡓࡵࡺࡩࡰࡰࡶࠫ৾"),
  bstack1llllll11_opy_ (u"ࠫࡸ࡫࠺ࡪࡧࡒࡴࡹ࡯࡯࡯ࡵࠪ৿"),
  bstack1llllll11_opy_ (u"ࠬࡹࡡࡧࡣࡵ࡭࠳ࡵࡰࡵ࡫ࡲࡲࡸ࠭਀"),
]
bstack1llll11l_opy_ = bstack11ll1l11l_opy_ + bstack11l1l1111_opy_ + bstack1lllll111_opy_
bstack1lllll_opy_ = [
  bstack1llllll11_opy_ (u"࠭࡞࡭ࡱࡦࡥࡱ࡮࡯ࡴࡶࠧࠫਁ"),
  bstack1llllll11_opy_ (u"ࠧ࡟ࡤࡶ࠱ࡱࡵࡣࡢ࡮࠱ࡧࡴࡳࠤࠨਂ"),
  bstack1llllll11_opy_ (u"ࠨࡠ࠴࠶࠼࠴ࠧਃ"),
  bstack1llllll11_opy_ (u"ࠩࡡ࠵࠵࠴ࠧ਄"),
  bstack1llllll11_opy_ (u"ࠪࡢ࠶࠽࠲࠯࠳࡞࠺࠲࠿࡝࠯ࠩਅ"),
  bstack1llllll11_opy_ (u"ࠫࡣ࠷࠷࠳࠰࠵࡟࠵࠳࠹࡞࠰ࠪਆ"),
  bstack1llllll11_opy_ (u"ࠬࡤ࠱࠸࠴࠱࠷ࡠ࠶࠭࠲࡟࠱ࠫਇ"),
  bstack1llllll11_opy_ (u"࠭࡞࠲࠻࠵࠲࠶࠼࠸࠯ࠩਈ")
]
bstack111ll11l_opy_ = bstack1llllll11_opy_ (u"ࠧࡩࡶࡷࡴࡸࡀ࠯࠰ࡣࡳ࡭࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡨࡵ࡭࠰ࡽࢀࠫਉ")
bstack1l1ll1l_opy_ = bstack1llllll11_opy_ (u"ࠨࡵࡧ࡯࠴ࡼ࠱࠰ࡧࡹࡩࡳࡺࠧਊ")
bstack1l11ll11_opy_ = [ bstack1llllll11_opy_ (u"ࠩࡤࡹࡹࡵ࡭ࡢࡶࡨࠫ਋") ]
bstack11lll11ll_opy_ = [ bstack1llllll11_opy_ (u"ࠪࡥࡵࡶ࠭ࡢࡷࡷࡳࡲࡧࡴࡦࠩ਌") ]
bstack1l1l11ll_opy_ = [ bstack1llllll11_opy_ (u"ࠫࡴࡨࡳࡦࡴࡹࡥࡧ࡯࡬ࡪࡶࡼࠫ਍") ]
bstack1111ll_opy_ = bstack1llllll11_opy_ (u"࡙ࠬࡄࡌࡕࡨࡸࡺࡶࠧ਎")
bstack1l1l1ll1_opy_ = bstack1llllll11_opy_ (u"࠭ࡓࡅࡍࡗࡩࡸࡺࡁࡵࡶࡨࡱࡵࡺࡥࡥࠩਏ")
bstack1l11l1lll_opy_ = bstack1llllll11_opy_ (u"ࠧࡔࡆࡎࡘࡪࡹࡴࡔࡷࡦࡧࡪࡹࡳࡧࡷ࡯ࠫਐ")
bstack1l1l1l1l_opy_ = bstack1llllll11_opy_ (u"ࠨ࠶࠱࠴࠳࠶ࠧ਑")
bstack1lll_opy_ = [
  bstack1llllll11_opy_ (u"ࠩࡈࡖࡗࡥࡆࡂࡋࡏࡉࡉ࠭਒"),
  bstack1llllll11_opy_ (u"ࠪࡉࡗࡘ࡟ࡕࡋࡐࡉࡉࡥࡏࡖࡖࠪਓ"),
  bstack1llllll11_opy_ (u"ࠫࡊࡘࡒࡠࡄࡏࡓࡈࡑࡅࡅࡡࡅ࡝ࡤࡉࡌࡊࡇࡑࡘࠬਔ"),
  bstack1llllll11_opy_ (u"ࠬࡋࡒࡓࡡࡑࡉ࡙࡝ࡏࡓࡍࡢࡇࡍࡇࡎࡈࡇࡇࠫਕ"),
  bstack1llllll11_opy_ (u"࠭ࡅࡓࡔࡢࡗࡔࡉࡋࡆࡖࡢࡒࡔ࡚࡟ࡄࡑࡑࡒࡊࡉࡔࡆࡆࠪਖ"),
  bstack1llllll11_opy_ (u"ࠧࡆࡔࡕࡣࡈࡕࡎࡏࡇࡆࡘࡎࡕࡎࡠࡅࡏࡓࡘࡋࡄࠨਗ"),
  bstack1llllll11_opy_ (u"ࠨࡇࡕࡖࡤࡉࡏࡏࡐࡈࡇ࡙ࡏࡏࡏࡡࡕࡉࡘࡋࡔࠨਘ"),
  bstack1llllll11_opy_ (u"ࠩࡈࡖࡗࡥࡃࡐࡐࡑࡉࡈ࡚ࡉࡐࡐࡢࡖࡊࡌࡕࡔࡇࡇࠫਙ"),
  bstack1llllll11_opy_ (u"ࠪࡉࡗࡘ࡟ࡄࡑࡑࡒࡊࡉࡔࡊࡑࡑࡣࡆࡈࡏࡓࡖࡈࡈࠬਚ"),
  bstack1llllll11_opy_ (u"ࠫࡊࡘࡒࡠࡅࡒࡒࡓࡋࡃࡕࡋࡒࡒࡤࡌࡁࡊࡎࡈࡈࠬਛ"),
  bstack1llllll11_opy_ (u"ࠬࡋࡒࡓࡡࡑࡅࡒࡋ࡟ࡏࡑࡗࡣࡗࡋࡓࡐࡎ࡙ࡉࡉ࠭ਜ"),
  bstack1llllll11_opy_ (u"࠭ࡅࡓࡔࡢࡅࡉࡊࡒࡆࡕࡖࡣࡎࡔࡖࡂࡎࡌࡈࠬਝ"),
  bstack1llllll11_opy_ (u"ࠧࡆࡔࡕࡣࡆࡊࡄࡓࡇࡖࡗࡤ࡛ࡎࡓࡇࡄࡇࡍࡇࡂࡍࡇࠪਞ"),
  bstack1llllll11_opy_ (u"ࠨࡇࡕࡖࡤ࡚ࡕࡏࡐࡈࡐࡤࡉࡏࡏࡐࡈࡇ࡙ࡏࡏࡏࡡࡉࡅࡎࡒࡅࡅࠩਟ"),
  bstack1llllll11_opy_ (u"ࠩࡈࡖࡗࡥࡃࡐࡐࡑࡉࡈ࡚ࡉࡐࡐࡢࡘࡎࡓࡅࡅࡡࡒ࡙࡙࠭ਠ"),
  bstack1llllll11_opy_ (u"ࠪࡉࡗࡘ࡟ࡔࡑࡆࡏࡘࡥࡃࡐࡐࡑࡉࡈ࡚ࡉࡐࡐࡢࡊࡆࡏࡌࡆࡆࠪਡ"),
  bstack1llllll11_opy_ (u"ࠫࡊࡘࡒࡠࡕࡒࡇࡐ࡙࡟ࡄࡑࡑࡒࡊࡉࡔࡊࡑࡑࡣࡍࡕࡓࡕࡡࡘࡒࡗࡋࡁࡄࡊࡄࡆࡑࡋࠧਢ"),
  bstack1llllll11_opy_ (u"ࠬࡋࡒࡓࡡࡓࡖࡔ࡞࡙ࡠࡅࡒࡒࡓࡋࡃࡕࡋࡒࡒࡤࡌࡁࡊࡎࡈࡈࠬਣ"),
  bstack1llllll11_opy_ (u"࠭ࡅࡓࡔࡢࡒࡆࡓࡅࡠࡐࡒࡘࡤࡘࡅࡔࡑࡏ࡚ࡊࡊࠧਤ"),
  bstack1llllll11_opy_ (u"ࠧࡆࡔࡕࡣࡓࡇࡍࡆࡡࡕࡉࡘࡕࡌࡖࡖࡌࡓࡓࡥࡆࡂࡋࡏࡉࡉ࠭ਥ"),
  bstack1llllll11_opy_ (u"ࠨࡇࡕࡖࡤࡓࡁࡏࡆࡄࡘࡔࡘ࡙ࡠࡒࡕࡓ࡝࡟࡟ࡄࡑࡑࡊࡎࡍࡕࡓࡃࡗࡍࡔࡔ࡟ࡇࡃࡌࡐࡊࡊࠧਦ"),
]
bstack1l111l_opy_ = bstack1llllll11_opy_ (u"ࠩ࠱࠳ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠰ࡥࡷࡺࡩࡧࡣࡦࡸࡸ࠵ࠧਧ")
def bstack1111l1l_opy_():
  global CONFIG
  headers = {
        bstack1llllll11_opy_ (u"ࠪࡇࡴࡴࡴࡦࡰࡷ࠱ࡹࡿࡰࡦࠩਨ"): bstack1llllll11_opy_ (u"ࠫࡦࡶࡰ࡭࡫ࡦࡥࡹ࡯࡯࡯࠱࡭ࡷࡴࡴࠧ਩"),
      }
  proxies = bstack1lll1l1l1_opy_(CONFIG, bstack1111l_opy_)
  try:
    response = requests.get(bstack1111l_opy_, headers=headers, proxies=proxies, timeout=5)
    if response.json():
      bstack11llll111_opy_ = response.json()[bstack1llllll11_opy_ (u"ࠬ࡮ࡵࡣࡵࠪਪ")]
      logger.debug(bstack111l1111l_opy_.format(response.json()))
      return bstack11llll111_opy_
    else:
      logger.debug(bstack1ll11lll_opy_.format(bstack1llllll11_opy_ (u"ࠨࡒࡦࡵࡳࡳࡳࡹࡥࠡࡌࡖࡓࡓࠦࡰࡢࡴࡶࡩࠥ࡫ࡲࡳࡱࡵࠤࠧਫ")))
  except Exception as e:
    logger.debug(bstack1ll11lll_opy_.format(e))
def bstack1lll11l1_opy_(hub_url):
  global CONFIG
  url = bstack1llllll11_opy_ (u"ࠢࡩࡶࡷࡴࡸࡀ࠯࠰ࠤਬ")+  hub_url + bstack1llllll11_opy_ (u"ࠣ࠱ࡦ࡬ࡪࡩ࡫ࠣਭ")
  headers = {
        bstack1llllll11_opy_ (u"ࠩࡆࡳࡳࡺࡥ࡯ࡶ࠰ࡸࡾࡶࡥࠨਮ"): bstack1llllll11_opy_ (u"ࠪࡥࡵࡶ࡬ࡪࡥࡤࡸ࡮ࡵ࡮࠰࡬ࡶࡳࡳ࠭ਯ"),
      }
  proxies = bstack1lll1l1l1_opy_(CONFIG, url)
  try:
    start_time = time.perf_counter()
    requests.get(url, headers=headers, proxies=proxies, timeout=5)
    latency = time.perf_counter() - start_time
    logger.debug(bstack111l1lll1_opy_.format(hub_url, latency))
    return dict(hub_url=hub_url, latency=latency)
  except Exception as e:
    logger.debug(bstack1l1111111_opy_.format(hub_url, e))
def bstack1l1ll1ll1_opy_():
  try:
    global bstack1l1111ll1_opy_
    bstack11llll111_opy_ = bstack1111l1l_opy_()
    bstack1ll111l1l_opy_ = []
    results = []
    for bstack11lll1ll1_opy_ in bstack11llll111_opy_:
      bstack1ll111l1l_opy_.append(bstack1l1lll111_opy_(target=bstack1lll11l1_opy_,args=(bstack11lll1ll1_opy_,)))
    for t in bstack1ll111l1l_opy_:
      t.start()
    for t in bstack1ll111l1l_opy_:
      results.append(t.join())
    bstack111l11111_opy_ = {}
    for item in results:
      hub_url = item[bstack1llllll11_opy_ (u"ࠫ࡭ࡻࡢࡠࡷࡵࡰࠬਰ")]
      latency = item[bstack1llllll11_opy_ (u"ࠬࡲࡡࡵࡧࡱࡧࡾ࠭਱")]
      bstack111l11111_opy_[hub_url] = latency
    bstack1lll111l1_opy_ = min(bstack111l11111_opy_, key= lambda x: bstack111l11111_opy_[x])
    bstack1l1111ll1_opy_ = bstack1lll111l1_opy_
    logger.debug(bstack1lll1lll_opy_.format(bstack1lll111l1_opy_))
  except Exception as e:
    logger.debug(bstack111ll1111_opy_.format(e))
bstack1ll1l11ll_opy_ = bstack1llllll11_opy_ (u"࠭ࡓࡦࡶࡷ࡭ࡳ࡭ࠠࡶࡲࠣࡪࡴࡸࠠࡃࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠲ࠠࡶࡵ࡬ࡲ࡬ࠦࡦࡳࡣࡰࡩࡼࡵࡲ࡬࠼ࠣࡿࢂ࠭ਲ")
bstack111lll_opy_ = bstack1llllll11_opy_ (u"ࠧࡄࡱࡰࡴࡱ࡫ࡴࡦࡦࠣࡷࡪࡺࡵࡱࠣࠪਲ਼")
bstack11l111lll_opy_ = bstack1llllll11_opy_ (u"ࠨࡒࡤࡶࡸ࡫ࡤࠡࡥࡲࡲ࡫࡯ࡧࠡࡨ࡬ࡰࡪࡀࠠࡼࡿࠪ਴")
bstack1l1llllll_opy_ = bstack1llllll11_opy_ (u"ࠩࡖࡥࡳ࡯ࡴࡪࡼࡨࡨࠥࡩ࡯࡯ࡨ࡬࡫ࠥ࡬ࡩ࡭ࡧ࠽ࠤࢀࢃࠧਵ")
bstack1lll1ll_opy_ = bstack1llllll11_opy_ (u"࡙ࠪࡸ࡯࡮ࡨࠢ࡫ࡹࡧࠦࡵࡳ࡮࠽ࠤࢀࢃࠧਸ਼")
bstack1l11l_opy_ = bstack1llllll11_opy_ (u"ࠫࡘ࡫ࡳࡴ࡫ࡲࡲࠥࡹࡴࡢࡴࡷࡩࡩࠦࡷࡪࡶ࡫ࠤ࡮ࡪ࠺ࠡࡽࢀࠫ਷")
bstack1llll1111_opy_ = bstack1llllll11_opy_ (u"ࠬࡘࡥࡤࡧ࡬ࡺࡪࡪࠠࡪࡰࡷࡩࡷࡸࡵࡱࡶ࠯ࠤࡪࡾࡩࡵ࡫ࡱ࡫ࠬਸ")
bstack111lll1ll_opy_ = bstack1llllll11_opy_ (u"࠭ࡐ࡭ࡧࡤࡷࡪࠦࡩ࡯ࡵࡷࡥࡱࡲࠠࡴࡧ࡯ࡩࡳ࡯ࡵ࡮ࠢࡷࡳࠥࡸࡵ࡯ࠢࡷࡩࡸࡺࡳ࠯ࠢࡣࡴ࡮ࡶࠠࡪࡰࡶࡸࡦࡲ࡬ࠡࡵࡨࡰࡪࡴࡩࡶ࡯ࡣࠫਹ")
bstack11ll1ll1l_opy_ = bstack1llllll11_opy_ (u"ࠧࡑ࡮ࡨࡥࡸ࡫ࠠࡪࡰࡶࡸࡦࡲ࡬ࠡࡲࡼࡸࡪࡹࡴࠡࡣࡱࡨࠥࡶࡹࡵࡧࡶࡸ࠲ࡹࡥ࡭ࡧࡱ࡭ࡺࡳࠠࡱࡣࡦ࡯ࡦ࡭ࡥࡴ࠰ࠣࡤࡵ࡯ࡰࠡ࡫ࡱࡷࡹࡧ࡬࡭ࠢࡳࡽࡹ࡫ࡳࡵࠢࡳࡽࡹ࡫ࡳࡵ࠯ࡶࡩࡱ࡫࡮ࡪࡷࡰࡤࠬ਺")
bstack11llll_opy_ = bstack1llllll11_opy_ (u"ࠨࡒ࡯ࡩࡦࡹࡥࠡ࡫ࡱࡷࡹࡧ࡬࡭ࠢࡄࡴࡵ࡯ࡵ࡮ࡎ࡬ࡦࡷࡧࡲࡺࠢࡳࡥࡨࡱࡡࡨࡧ࠱ࠤࡥࡶࡩࡱࠢ࡬ࡲࡸࡺࡡ࡭࡮ࠣࡶࡴࡨ࡯ࡵࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮࠱ࡦࡶࡰࡪࡷࡰࡰ࡮ࡨࡲࡢࡴࡼࡤࠬ਻")
bstack1ll1111ll_opy_ = bstack1llllll11_opy_ (u"ࠩࡓࡰࡪࡧࡳࡦࠢ࡬ࡲࡸࡺࡡ࡭࡮ࠣࡶࡴࡨ࡯ࡵ࠮ࠣࡴࡦࡨ࡯ࡵࠢࡤࡲࡩࠦࡳࡦ࡮ࡨࡲ࡮ࡻ࡭࡭࡫ࡥࡶࡦࡸࡹࠡࡲࡤࡧࡰࡧࡧࡦࡵࠣࡸࡴࠦࡲࡶࡰࠣࡶࡴࡨ࡯ࡵࠢࡷࡩࡸࡺࡳࠡ࡫ࡱࠤࡵࡧࡲࡢ࡮࡯ࡩࡱ࠴ࠠࡡࡲ࡬ࡴࠥ࡯࡮ࡴࡶࡤࡰࡱࠦࡲࡰࡤࡲࡸ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࠠࡳࡱࡥࡳࡹ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫࠮ࡲࡤࡦࡴࡺࠠࡳࡱࡥࡳࡹ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫࠮ࡵࡨࡰࡪࡴࡩࡶ࡯࡯࡭ࡧࡸࡡࡳࡻࡣ਼ࠫ")
bstack11ll111_opy_ = bstack1llllll11_opy_ (u"ࠪࡔࡱ࡫ࡡࡴࡧࠣ࡭ࡳࡹࡴࡢ࡮࡯ࠤࡧ࡫ࡨࡢࡸࡨࠤࡹࡵࠠࡳࡷࡱࠤࡹ࡫ࡳࡵࡵ࠱ࠤࡥࡶࡩࡱࠢ࡬ࡲࡸࡺࡡ࡭࡮ࠣࡦࡪ࡮ࡡࡷࡧࡣࠫ਽")
bstack1l11l111_opy_ = bstack1llllll11_opy_ (u"ࠫࡕࡲࡥࡢࡵࡨࠤ࡮ࡴࡳࡵࡣ࡯ࡰࠥࡧࡰࡱ࡫ࡸࡱ࠲ࡩ࡬ࡪࡧࡱࡸࠥࡺ࡯ࠡࡴࡸࡲࠥࡺࡥࡴࡶࡶ࠲ࠥࡦࡰࡪࡲࠣ࡭ࡳࡹࡴࡢ࡮࡯ࠤࡆࡶࡰࡪࡷࡰ࠱ࡕࡿࡴࡩࡱࡱ࠱ࡈࡲࡩࡦࡰࡷࡤࠬਾ")
bstack1llll_opy_ = bstack1llllll11_opy_ (u"ࠬࡖ࡬ࡦࡣࡶࡩࠥ࡯࡮ࡴࡶࡤࡰࡱࠦࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࠣࡸࡴࠦࡲࡶࡰࠣࡸࡪࡹࡴࡴ࠰ࠣࡤࡵ࡯ࡰࠡ࡫ࡱࡷࡹࡧ࡬࡭ࠢࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹࡦࠧਿ")
bstack11111l1l_opy_ = bstack1llllll11_opy_ (u"࠭ࡃࡰࡷ࡯ࡨࠥࡴ࡯ࡵࠢࡩ࡭ࡳࡪࠠࡦ࡫ࡷ࡬ࡪࡸࠠࡔࡧ࡯ࡩࡳ࡯ࡵ࡮ࠢࡲࡶࠥࡖ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠢࡷࡳࠥࡸࡵ࡯ࠢࡷࡩࡸࡺࡳ࠯ࠢࡓࡰࡪࡧࡳࡦࠢ࡬ࡲࡹࡧ࡬࡭ࠢࡷ࡬ࡪࠦࡲࡦ࡮ࡨࡺࡦࡴࡴࠡࡲࡤࡧࡰࡧࡧࡦࡵࠣࡹࡸ࡯࡮ࡨࠢࡳ࡭ࡵࠦࡴࡰࠢࡵࡹࡳࠦࡴࡦࡵࡷࡷ࠳࠭ੀ")
bstack1lll1l1l_opy_ = bstack1llllll11_opy_ (u"ࠧࡉࡣࡱࡨࡱ࡯࡮ࡨࠢࡶࡩࡸࡹࡩࡰࡰࠣࡧࡱࡵࡳࡦࠩੁ")
bstack1l11lll11_opy_ = bstack1llllll11_opy_ (u"ࠨࡃ࡯ࡰࠥࡪ࡯࡯ࡧࠤࠫੂ")
bstack111l1ll1_opy_ = bstack1llllll11_opy_ (u"ࠩࡆࡳࡳ࡬ࡩࡨࠢࡩ࡭ࡱ࡫ࠠࡥࡱࡨࡷࠥࡴ࡯ࡵࠢࡨࡼ࡮ࡹࡴࠡࡣࡷࠤࡦࡴࡹࠡࡲࡤࡶࡪࡴࡴࠡࡦ࡬ࡶࡪࡩࡴࡰࡴࡼࠤࡴ࡬ࠠࠣࡽࢀࠦ࠳ࠦࡐ࡭ࡧࡤࡷࡪࠦࡩ࡯ࡥ࡯ࡹࡩ࡫ࠠࡢࠢࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡻࡰࡰ࠴ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡾࡧ࡭࡭ࠢࡩ࡭ࡱ࡫ࠠࡤࡱࡱࡸࡦ࡯࡮ࡪࡰࡪࠤࡨࡵ࡮ࡧ࡫ࡪࡹࡷࡧࡴࡪࡱࡱࠤ࡫ࡵࡲࠡࡶࡨࡷࡹࡹ࠮ࠨ੃")
bstack1ll1ll1_opy_ = bstack1llllll11_opy_ (u"ࠪࡆࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠢࡦࡶࡪࡪࡥ࡯ࡶ࡬ࡥࡱࡹࠠ࡯ࡱࡷࠤࡵࡸ࡯ࡷ࡫ࡧࡩࡩ࠴ࠠࡑ࡮ࡨࡥࡸ࡫ࠠࡢࡦࡧࠤࡹ࡮ࡥ࡮ࠢ࡬ࡲࠥࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡾࡳ࡬ࠡࡥࡲࡲ࡫࡯ࡧࠡࡨ࡬ࡰࡪࠦࡡࡴࠢࠥࡹࡸ࡫ࡲࡏࡣࡰࡩࠧࠦࡡ࡯ࡦࠣࠦࡦࡩࡣࡦࡵࡶࡏࡪࡿࠢࠡࡱࡵࠤࡸ࡫ࡴࠡࡶ࡫ࡩࡲࠦࡡࡴࠢࡨࡲࡻ࡯ࡲࡰࡰࡰࡩࡳࡺࠠࡷࡣࡵ࡭ࡦࡨ࡬ࡦࡵ࠽ࠤࠧࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡚࡙ࡅࡓࡐࡄࡑࡊࠨࠠࡢࡰࡧࠤࠧࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡆࡉࡃࡆࡕࡖࡣࡐࡋ࡙ࠣࠩ੄")
bstack1l11l1l1_opy_ = bstack1llllll11_opy_ (u"ࠫࡒࡧ࡬ࡧࡱࡵࡱࡪࡪࠠࡤࡱࡱࡪ࡮࡭ࠠࡧ࡫࡯ࡩ࠿ࠨࡻࡾࠤࠪ੅")
bstack11lllll1l_opy_ = bstack1llllll11_opy_ (u"ࠬࡋ࡮ࡤࡱࡸࡲࡹ࡫ࡲࡦࡦࠣࡩࡷࡸ࡯ࡳࠢࡺ࡬࡮ࡲࡥࠡࡵࡨࡸࡹ࡯࡮ࡨࠢࡸࡴࠥ࠳ࠠࡼࡿࠪ੆")
bstack1llll1_opy_ = bstack1llllll11_opy_ (u"࠭ࡓࡵࡣࡵࡸ࡮ࡴࡧࠡࡄࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠠࡍࡱࡦࡥࡱ࠭ੇ")
bstack11l1l1ll_opy_ = bstack1llllll11_opy_ (u"ࠧࡔࡶࡲࡴࡵ࡯࡮ࡨࠢࡅࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠡࡎࡲࡧࡦࡲࠧੈ")
bstack1lllll11l_opy_ = bstack1llllll11_opy_ (u"ࠨࡄࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠠࡍࡱࡦࡥࡱࠦࡩࡴࠢࡱࡳࡼࠦࡲࡶࡰࡱ࡭ࡳ࡭ࠡࠨ੉")
bstack1ll1l1l1l_opy_ = bstack1llllll11_opy_ (u"ࠩࡆࡳࡺࡲࡤࠡࡰࡲࡸࠥࡹࡴࡢࡴࡷࠤࡇࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠣࡐࡴࡩࡡ࡭࠼ࠣࡿࢂ࠭੊")
bstack11l11lll_opy_ = bstack1llllll11_opy_ (u"ࠪࡗࡹࡧࡲࡵ࡫ࡱ࡫ࠥࡲ࡯ࡤࡣ࡯ࠤࡧ࡯࡮ࡢࡴࡼࠤࡼ࡯ࡴࡩࠢࡲࡴࡹ࡯࡯࡯ࡵ࠽ࠤࢀࢃࠧੋ")
bstack11ll1l111_opy_ = bstack1llllll11_opy_ (u"࡚ࠫࡶࡤࡢࡶ࡬ࡲ࡬ࠦࡳࡦࡵࡶ࡭ࡴࡴࠠࡥࡧࡷࡥ࡮ࡲࡳ࠻ࠢࡾࢁࠬੌ")
bstack11ll111l_opy_ = bstack1llllll11_opy_ (u"ࠬࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡴࡧࡷࡸ࡮ࡴࡧࠡࡷࡳࡨࡦࡺࡩ࡯ࡩࠣࡸࡪࡹࡴࠡࡵࡷࡥࡹࡻࡳࠡࡽࢀ੍ࠫ")
bstack1lllll1ll_opy_ = bstack1llllll11_opy_ (u"࠭ࡐ࡭ࡧࡤࡷࡪࠦࡰࡳࡱࡹ࡭ࡩ࡫ࠠࡢࡰࠣࡥࡵࡶࡲࡰࡲࡵ࡭ࡦࡺࡥࠡࡈ࡚ࠤ࠭ࡸ࡯ࡣࡱࡷ࠳ࡵࡧࡢࡰࡶࠬࠤ࡮ࡴࠠࡤࡱࡱࡪ࡮࡭ࠠࡧ࡫࡯ࡩ࠱ࠦࡳ࡬࡫ࡳࠤࡹ࡮ࡥࠡࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࠤࡰ࡫ࡹࠡ࡫ࡱࠤࡨࡵ࡮ࡧ࡫ࡪࠤ࡮࡬ࠠࡳࡷࡱࡲ࡮ࡴࡧࠡࡵ࡬ࡱࡵࡲࡥࠡࡲࡼࡸ࡭ࡵ࡮ࠡࡵࡦࡶ࡮ࡶࡴࠡࡹ࡬ࡸ࡭ࡵࡵࡵࠢࡤࡲࡾࠦࡆࡘ࠰ࠪ੎")
bstack11llll11l_opy_ = bstack1llllll11_opy_ (u"ࠧࡔࡧࡷࡸ࡮ࡴࡧࠡࡪࡷࡸࡵࡖࡲࡰࡺࡼ࠳࡭ࡺࡴࡱࡵࡓࡶࡴࡾࡹࠡ࡫ࡶࠤࡳࡵࡴࠡࡵࡸࡴࡵࡵࡲࡵࡧࡧࠤࡴࡴࠠࡤࡷࡵࡶࡪࡴࡴ࡭ࡻࠣ࡭ࡳࡹࡴࡢ࡮࡯ࡩࡩࠦࡶࡦࡴࡶ࡭ࡴࡴࠠࡰࡨࠣࡷࡪࡲࡥ࡯࡫ࡸࡱࠥ࠮ࡻࡾࠫ࠯ࠤࡵࡲࡥࡢࡵࡨࠤࡺࡶࡧࡳࡣࡧࡩࠥࡺ࡯ࠡࡕࡨࡰࡪࡴࡩࡶ࡯ࡁࡁ࠹࠴࠰࠯࠲ࠣࡳࡷࠦࡲࡦࡨࡨࡶࠥࡺ࡯ࠡࡪࡷࡸࡵࡹ࠺࠰࠱ࡺࡻࡼ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮࠱ࡧࡳࡨࡹ࠯ࡢࡷࡷࡳࡲࡧࡴࡦ࠱ࡶࡩࡱ࡫࡮ࡪࡷࡰ࠳ࡷࡻ࡮࠮ࡶࡨࡷࡹࡹ࠭ࡣࡧ࡫࡭ࡳࡪ࠭ࡱࡴࡲࡼࡾࠩࡰࡺࡶ࡫ࡳࡳࠦࡦࡰࡴࠣࡥࠥࡽ࡯ࡳ࡭ࡤࡶࡴࡻ࡮ࡥ࠰ࠪ੏")
bstack1l11111l1_opy_ = bstack1llllll11_opy_ (u"ࠨࡉࡨࡲࡪࡸࡡࡵ࡫ࡱ࡫ࠥࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠤࡨࡵ࡮ࡧ࡫ࡪࡹࡷࡧࡴࡪࡱࡱࠤࡾࡳ࡬ࠡࡨ࡬ࡰࡪ࠴࠮ࠨ੐")
bstack111111l_opy_ = bstack1llllll11_opy_ (u"ࠩࡖࡹࡨࡩࡥࡴࡵࡩࡹࡱࡲࡹࠡࡩࡨࡲࡪࡸࡡࡵࡧࡧࠤࡹ࡮ࡥࠡࡥࡲࡲ࡫࡯ࡧࡶࡴࡤࡸ࡮ࡵ࡮ࠡࡨ࡬ࡰࡪࠧࠧੑ")
bstack1ll1l1l11_opy_ = bstack1llllll11_opy_ (u"ࠪࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡧࡦࡰࡨࡶࡦࡺࡥࠡࡶ࡫ࡩࠥࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠤࡨࡵ࡮ࡧ࡫ࡪࡹࡷࡧࡴࡪࡱࡱࠤ࡫࡯࡬ࡦ࠰ࠣࡿࢂ࠭੒")
bstack11l11ll1l_opy_ = bstack1llllll11_opy_ (u"ࠫࡊࡾࡰࡦࡥࡷࡩࡩࠦࡡࡵࠢ࡯ࡩࡦࡹࡴࠡ࠳ࠣ࡭ࡳࡶࡵࡵ࠮ࠣࡶࡪࡩࡥࡪࡸࡨࡨࠥ࠶ࠧ੓")
bstack1l_opy_ = bstack1llllll11_opy_ (u"ࠬࡋࡲࡳࡱࡵࠤࡩࡻࡲࡪࡰࡪࠤࡆࡶࡰࠡࡷࡳࡰࡴࡧࡤ࠯ࠢࡾࢁࠬ੔")
bstack1l1lllll1_opy_ = bstack1llllll11_opy_ (u"࠭ࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡸࡴࡱࡵࡡࡥࠢࡄࡴࡵ࠴ࠠࡊࡰࡹࡥࡱ࡯ࡤࠡࡨ࡬ࡰࡪࠦࡰࡢࡶ࡫ࠤࡵࡸ࡯ࡷ࡫ࡧࡩࡩࠦࡻࡾ࠰ࠪ੕")
bstack1l11lllll_opy_ = bstack1llllll11_opy_ (u"ࠧࡌࡧࡼࡷࠥࡩࡡ࡯ࡰࡲࡸࠥࡩ࡯࠮ࡧࡻ࡭ࡸࡺࠠࡢࡵࠣࡥࡵࡶࠠࡷࡣ࡯ࡹࡪࡹࠬࠡࡷࡶࡩࠥࡧ࡮ࡺࠢࡲࡲࡪࠦࡰࡳࡱࡳࡩࡷࡺࡹࠡࡨࡵࡳࡲࠦࡻࡪࡦ࠿ࡷࡹࡸࡩ࡯ࡩࡁ࠰ࠥࡶࡡࡵࡪ࠿ࡷࡹࡸࡩ࡯ࡩࡁ࠰ࠥࡩࡵࡴࡶࡲࡱࡤ࡯ࡤ࠽ࡵࡷࡶ࡮ࡴࡧ࠿࠮ࠣࡷ࡭ࡧࡲࡦࡣࡥࡰࡪࡥࡩࡥ࠾ࡶࡸࡷ࡯࡮ࡨࡀࢀ࠰ࠥࡵ࡮࡭ࡻࠣࠦࡵࡧࡴࡩࠤࠣࡥࡳࡪࠠࠣࡥࡸࡷࡹࡵ࡭ࡠ࡫ࡧࠦࠥࡩࡡ࡯ࠢࡦࡳ࠲࡫ࡸࡪࡵࡷࠤࡹࡵࡧࡦࡶ࡫ࡩࡷ࠴ࠧ੖")
bstack11llllll_opy_ = bstack1llllll11_opy_ (u"ࠨ࡝ࡌࡲࡻࡧ࡬ࡪࡦࠣࡥࡵࡶࠠࡱࡴࡲࡴࡪࡸࡴࡺ࡟ࠣࡷࡺࡶࡰࡰࡴࡷࡩࡩࠦࡰࡳࡱࡳࡩࡷࡺࡩࡦࡵࠣࡥࡷ࡫ࠠࡼ࡫ࡧࡀࡸࡺࡲࡪࡰࡪࡂ࠱ࠦࡰࡢࡶ࡫ࡀࡸࡺࡲࡪࡰࡪࡂ࠱ࠦࡣࡶࡵࡷࡳࡲࡥࡩࡥ࠾ࡶࡸࡷ࡯࡮ࡨࡀ࠯ࠤࡸ࡮ࡡࡳࡧࡤࡦࡱ࡫࡟ࡪࡦ࠿ࡷࡹࡸࡩ࡯ࡩࡁࢁ࠳ࠦࡆࡰࡴࠣࡱࡴࡸࡥࠡࡦࡨࡸࡦ࡯࡬ࡴࠢࡳࡰࡪࡧࡳࡦࠢࡹ࡭ࡸ࡯ࡴࠡࡪࡷࡸࡵࡹ࠺࠰࠱ࡺࡻࡼ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮࠱ࡧࡳࡨࡹ࠯ࡢࡲࡳ࠱ࡦࡻࡴࡰ࡯ࡤࡸࡪ࠵ࡡࡱࡲ࡬ࡹࡲ࠵ࡳࡦࡶ࠰ࡹࡵ࠳ࡴࡦࡵࡷࡷ࠴ࡹࡰࡦࡥ࡬ࡪࡾ࠳ࡡࡱࡲࠪ੗")
bstack1ll11l1l_opy_ = bstack1llllll11_opy_ (u"ࠩ࡞ࡍࡳࡼࡡ࡭࡫ࡧࠤࡦࡶࡰࠡࡲࡵࡳࡵ࡫ࡲࡵࡻࡠࠤࡘࡻࡰࡱࡱࡵࡸࡪࡪࠠࡷࡣ࡯ࡹࡪࡹࠠࡰࡨࠣࡥࡵࡶࠠࡢࡴࡨࠤࡴ࡬ࠠࡼ࡫ࡧࡀࡸࡺࡲࡪࡰࡪࡂ࠱ࠦࡰࡢࡶ࡫ࡀࡸࡺࡲࡪࡰࡪࡂ࠱ࠦࡣࡶࡵࡷࡳࡲࡥࡩࡥ࠾ࡶࡸࡷ࡯࡮ࡨࡀ࠯ࠤࡸ࡮ࡡࡳࡧࡤࡦࡱ࡫࡟ࡪࡦ࠿ࡷࡹࡸࡩ࡯ࡩࡁࢁ࠳ࠦࡆࡰࡴࠣࡱࡴࡸࡥࠡࡦࡨࡸࡦ࡯࡬ࡴࠢࡳࡰࡪࡧࡳࡦࠢࡹ࡭ࡸ࡯ࡴࠡࡪࡷࡸࡵࡹ࠺࠰࠱ࡺࡻࡼ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮࠱ࡧࡳࡨࡹ࠯ࡢࡲࡳ࠱ࡦࡻࡴࡰ࡯ࡤࡸࡪ࠵ࡡࡱࡲ࡬ࡹࡲ࠵ࡳࡦࡶ࠰ࡹࡵ࠳ࡴࡦࡵࡷࡷ࠴ࡹࡰࡦࡥ࡬ࡪࡾ࠳ࡡࡱࡲࠪ੘")
bstack1_opy_ = bstack1llllll11_opy_ (u"࡙ࠪࡸ࡯࡮ࡨࠢࡨࡼ࡮ࡹࡴࡪࡰࡪࠤࡦࡶࡰࠡ࡫ࡧࠤࢀࢃࠠࡧࡱࡵࠤ࡭ࡧࡳࡩࠢ࠽ࠤࢀࢃ࠮ࠨਖ਼")
bstack1ll111111_opy_ = bstack1llllll11_opy_ (u"ࠫࡆࡶࡰࠡࡗࡳࡰࡴࡧࡤࡦࡦࠣࡗࡺࡩࡣࡦࡵࡶࡪࡺࡲ࡬ࡺ࠰ࠣࡍࡉࠦ࠺ࠡࡽࢀࠫਗ਼")
bstack1ll11111_opy_ = bstack1llllll11_opy_ (u"࡛ࠬࡳࡪࡰࡪࠤࡆࡶࡰࠡ࠼ࠣࡿࢂ࠴ࠧਜ਼")
bstack1l11l1ll1_opy_ = bstack1llllll11_opy_ (u"࠭ࡰࡢࡴࡤࡰࡱ࡫࡬ࡴࡒࡨࡶࡕࡲࡡࡵࡨࡲࡶࡲࠦࡩࡴࠢࡱࡳࡹࠦࡳࡶࡲࡳࡳࡷࡺࡥࡥࠢࡩࡳࡷࠦࡶࡢࡰ࡬ࡰࡱࡧࠠࡱࡻࡷ࡬ࡴࡴࠠࡵࡧࡶࡸࡸ࠲ࠠࡳࡷࡱࡲ࡮ࡴࡧࠡࡹ࡬ࡸ࡭ࠦࡰࡢࡴࡤࡰࡱ࡫࡬ࡑࡧࡵࡔࡱࡧࡴࡧࡱࡵࡱࠥࡃࠠ࠲ࠩੜ")
bstack1l1111l11_opy_ = bstack1llllll11_opy_ (u"ࠧࡆࡴࡵࡳࡷࠦࡩ࡯ࠢࡦࡶࡪࡧࡴࡪࡰࡪࠤࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷࡀࠠࡼࡿࠪ੝")
bstack1lllllll_opy_ = bstack1llllll11_opy_ (u"ࠨࡅࡲࡹࡱࡪࠠ࡯ࡱࡷࠤࡨࡲ࡯ࡴࡧࠣࡦࡷࡵࡷࡴࡧࡵ࠾ࠥࢁࡽࠨਫ਼")
bstack1l1l1l1l1_opy_ = bstack1llllll11_opy_ (u"ࠩࡆࡳࡺࡲࡤࠡࡰࡲࡸࠥ࡭ࡥࡵࠢࡵࡩࡦࡹ࡯࡯ࠢࡩࡳࡷࠦࡢࡦࡪࡤࡺࡪࠦࡦࡦࡣࡷࡹࡷ࡫ࠠࡧࡣ࡬ࡰࡺࡸࡥ࠯ࠢࡾࢁࠬ੟")
bstack1l1111_opy_ = bstack1llllll11_opy_ (u"ࠪࡉࡷࡸ࡯ࡳࠢࡺ࡬࡮ࡲࡥࠡࡩࡨࡸࡹ࡯࡮ࡨࠢࡵࡩࡸࡶ࡯࡯ࡵࡨࠤ࡫ࡸ࡯࡮ࠢࡤࡴ࡮ࠦࡣࡢ࡮࡯࠲ࠥࡋࡲࡳࡱࡵ࠾ࠥࢁࡽࠨ੠")
bstack1l11l11ll_opy_ = bstack1llllll11_opy_ (u"࡚ࠫࡴࡡࡣ࡮ࡨࠤࡹࡵࠠࡴࡪࡲࡻࠥࡨࡵࡪ࡮ࡧࠤ࡚ࡘࡌ࠭ࠢࡤࡷࠥࡨࡵࡪ࡮ࡧࠤࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡹࠡ࡫ࡶࠤࡳࡵࡴࠡࡷࡶࡩࡩ࠴ࠧ੡")
bstack1ll1l111_opy_ = bstack1llllll11_opy_ (u"࡙ࠬࡥࡳࡸࡨࡶࠥࡹࡩࡥࡧࠣࡦࡺ࡯࡬ࡥࡐࡤࡱࡪ࠮ࡻࡾࠫࠣ࡭ࡸࠦ࡮ࡰࡶࠣࡷࡦࡳࡥࠡࡣࡶࠤࡨࡲࡩࡦࡰࡷࠤࡸ࡯ࡤࡦࠢࡥࡹ࡮ࡲࡤࡏࡣࡰࡩ࠭ࢁࡽࠪࠩ੢")
bstack1l1ll1l1_opy_ = bstack1llllll11_opy_ (u"࠭ࡖࡪࡧࡺࠤࡧࡻࡩ࡭ࡦࠣࡳࡳࠦࡂࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࠥࡪࡡࡴࡪࡥࡳࡦࡸࡤ࠻ࠢࡾࢁࠬ੣")
bstack11lll111_opy_ = bstack1llllll11_opy_ (u"ࠧࡖࡰࡤࡦࡱ࡫ࠠࡵࡱࠣࡥࡨࡩࡥࡴࡵࠣࡥࠥࡶࡲࡪࡸࡤࡸࡪࠦࡤࡰ࡯ࡤ࡭ࡳࡀࠠࡼࡿࠣ࠲࡙ࠥࡥࡵࠢࡷ࡬ࡪࠦࡦࡰ࡮࡯ࡳࡼ࡯࡮ࡨࠢࡦࡳࡳ࡬ࡩࡨࠢ࡬ࡲࠥࡿ࡯ࡶࡴࠣࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡼࡱࡱࠦࡦࡪ࡮ࡨ࠾ࠥࡢ࡮࠮࠯࠰࠱࠲࠳࠭࠮࠯࠰࠱ࠥࡢ࡮ࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡌࡰࡥࡤࡰ࠿ࠦࡴࡳࡷࡨࠤࡡࡴ࠭࠮࠯࠰࠱࠲࠳࠭࠮࠯࠰ࠫ੤")
bstack11lll_opy_ = bstack1llllll11_opy_ (u"ࠨࡕࡲࡱࡪࡺࡨࡪࡰࡪࠤࡼ࡫࡮ࡵࠢࡺࡶࡴࡴࡧࠡࡹ࡫࡭ࡱ࡫ࠠࡦࡺࡨࡧࡺࡺࡩ࡯ࡩࠣ࡫ࡪࡺ࡟࡯ࡷࡧ࡫ࡪࡥ࡬ࡰࡥࡤࡰࡤ࡫ࡲࡳࡱࡵࠤ࠿ࠦࡻࡾࠩ੥")
bstack1l111l1_opy_ = bstack1llllll11_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡸ࡫࡮ࡥࡡࡤࡱࡵࡲࡩࡵࡷࡧࡩࡤ࡫ࡶࡦࡰࡷࠤ࡫ࡵࡲࠡࡕࡇࡏࡘ࡫ࡴࡶࡲࠣࡿࢂࠨ੦")
bstack1111l1ll_opy_ = bstack1llllll11_opy_ (u"ࠥࡉࡷࡸ࡯ࡳࠢ࡬ࡲࠥࡹࡥ࡯ࡦࡢࡥࡲࡶ࡬ࡪࡶࡸࡨࡪࡥࡥࡷࡧࡱࡸࠥ࡬࡯ࡳࠢࡖࡈࡐ࡚ࡥࡴࡶࡄࡸࡹ࡫࡭ࡱࡶࡨࡨࠥࢁࡽࠣ੧")
bstack1111l1_opy_ = bstack1llllll11_opy_ (u"ࠦࡊࡸࡲࡰࡴࠣ࡭ࡳࠦࡳࡦࡰࡧࡣࡦࡳࡰ࡭࡫ࡷࡹࡩ࡫࡟ࡦࡸࡨࡲࡹࠦࡦࡰࡴࠣࡗࡉࡑࡔࡦࡵࡷࡗࡺࡩࡣࡦࡵࡶࡪࡺࡲࠠࡼࡿࠥ੨")
bstack1l1llll11_opy_ = bstack1llllll11_opy_ (u"ࠧࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡧ࡫ࡵࡩࡤࡸࡥࡲࡷࡨࡷࡹࠦࡻࡾࠤ੩")
bstack1lll1111_opy_ = bstack1llllll11_opy_ (u"ࠨࡐࡐࡕࡗࠤࡊࡼࡥ࡯ࡶࠣࡿࢂࠦࡲࡦࡵࡳࡳࡳࡹࡥࠡ࠼ࠣࡿࢂࠨ੪")
bstack11l1111l1_opy_ = bstack1llllll11_opy_ (u"ࠧࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡧࡴࡴࡦࡪࡩࡸࡶࡪࠦࡰࡳࡱࡻࡽࠥࡹࡥࡵࡶ࡬ࡲ࡬ࡹࠬࠡࡧࡵࡶࡴࡸ࠺ࠡࡽࢀࠫ੫")
bstack111l1111l_opy_ = bstack1llllll11_opy_ (u"ࠨࡔࡨࡷࡵࡵ࡮ࡴࡧࠣࡪࡷࡵ࡭ࠡ࠱ࡱࡩࡽࡺ࡟ࡩࡷࡥࡷࠥࢁࡽࠨ੬")
bstack1ll11lll_opy_ = bstack1llllll11_opy_ (u"ࠩࡈࡶࡷࡵࡲࠡ࡫ࡱࠤ࡬࡫ࡴࡵ࡫ࡱ࡫ࠥࡸࡥࡴࡲࡲࡲࡸ࡫ࠠࡧࡴࡲࡱࠥ࠵࡮ࡦࡺࡷࡣ࡭ࡻࡢࡴ࠼ࠣࡿࢂ࠭੭")
bstack1lll1lll_opy_ = bstack1llllll11_opy_ (u"ࠪࡒࡪࡧࡲࡦࡵࡷࠤ࡭ࡻࡢࠡࡣ࡯ࡰࡴࡩࡡࡵࡧࡧࠤ࡮ࡹ࠺ࠡࡽࢀࠫ੮")
bstack111ll1111_opy_ = bstack1llllll11_opy_ (u"ࠫࡊࡘࡒࡐࡔࠣࡍࡓࠦࡁࡍࡎࡒࡇࡆ࡚ࡅࠡࡊࡘࡆࠥࢁࡽࠨ੯")
bstack111l1lll1_opy_ = bstack1llllll11_opy_ (u"ࠬࡒࡡࡵࡧࡱࡧࡾࠦ࡯ࡧࠢ࡫ࡹࡧࡀࠠࡼࡿࠣ࡭ࡸࡀࠠࡼࡿࠪੰ")
bstack1l1111111_opy_ = bstack1llllll11_opy_ (u"࠭ࡅࡳࡴࡲࡶࠥ࡯࡮ࠡࡩࡨࡸࡹ࡯࡮ࡨࠢ࡯ࡥࡹ࡫࡮ࡤࡻࠣࡪࡴࡸࠠࡼࡿࠣ࡬ࡺࡨ࠺ࠡࡽࢀࠫੱ")
bstack111lll1l_opy_ = bstack1llllll11_opy_ (u"ࠧࡉࡷࡥࠤࡺࡸ࡬ࠡࡥ࡫ࡥࡳ࡭ࡥࡥࠢࡷࡳࠥࡺࡨࡦࠢࡲࡴࡹ࡯࡭ࡢ࡮ࠣ࡬ࡺࡨ࠺ࠡࡽࢀࠫੲ")
bstack1l1ll1l1l_opy_ = bstack1llllll11_opy_ (u"ࠨࡇࡵࡶࡴࡸࠠࡸࡪ࡬ࡰࡪࠦࡳࡦࡶࡷ࡭ࡳ࡭ࠠࡵࡪࡨࠤࡴࡶࡴࡪ࡯ࡤࡰࠥ࡮ࡵࡣࠢࡸࡶࡱࡀࠠࡼࡿࠪੳ")
bstack1l11ll1l1_opy_ = bstack1llllll11_opy_ (u"ࠩࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥ࡭ࡥࡵࠢࡶࡩࡸࡹࡩࡰࡰࠣࡰ࡮ࡹࡴࡴ࠼ࠣࡿࢂ࠭ੴ")
bstack1l11llll_opy_ = bstack1llllll11_opy_ (u"ࠪࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡧࡦࡰࡨࡶࡦࡺࡥࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠠࡣࡷ࡬ࡰࡩࠦࡡࡳࡶ࡬ࡪࡦࡩࡴࡴ࠼ࠣࡿࢂ࠭ੵ")
bstack111l1l11_opy_ = bstack1llllll11_opy_ (u"࡚ࠫࡴࡡࡣ࡮ࡨࠤࡹࡵࠠࡱࡣࡵࡷࡪࠦࡰࡢࡥࠣࡪ࡮ࡲࡥࠡࡽࢀ࠲ࠥࡋࡲࡳࡱࡵࠤ࠲ࠦࡻࡾࠩ੶")
bstack1111llll1_opy_ = bstack1llllll11_opy_ (u"ࠬࠦࠠ࠰ࠬࠣࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃࠠࠫ࠱࡟ࡲࠥࠦࡩࡧࠪࡳࡥ࡬࡫ࠠ࠾࠿ࡀࠤࡻࡵࡩࡥࠢ࠳࠭ࠥࢁ࡜࡯ࠢࠣࠤࡹࡸࡹࡼ࡞ࡱࠤࡨࡵ࡮ࡴࡶࠣࡪࡸࠦ࠽ࠡࡴࡨࡵࡺ࡯ࡲࡦࠪ࡟ࠫ࡫ࡹ࡜ࠨࠫ࠾ࡠࡳࠦࠠࠡࠢࠣࡪࡸ࠴ࡡࡱࡲࡨࡲࡩࡌࡩ࡭ࡧࡖࡽࡳࡩࠨࡣࡵࡷࡥࡨࡱ࡟ࡱࡣࡷ࡬࠱ࠦࡊࡔࡑࡑ࠲ࡸࡺࡲࡪࡰࡪ࡭࡫ࡿࠨࡱࡡ࡬ࡲࡩ࡫ࡸࠪࠢ࠮ࠤࠧࡀࠢࠡ࠭ࠣࡎࡘࡕࡎ࠯ࡵࡷࡶ࡮ࡴࡧࡪࡨࡼࠬࡏ࡙ࡏࡏ࠰ࡳࡥࡷࡹࡥࠩࠪࡤࡻࡦ࡯ࡴࠡࡰࡨࡻࡕࡧࡧࡦ࠴࠱ࡩࡻࡧ࡬ࡶࡣࡷࡩ࠭ࠨࠨࠪࠢࡀࡂࠥࢁࡽࠣ࠮ࠣࡠࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࠤࡤࡧࡹ࡯࡯࡯ࠤ࠽ࠤࠧ࡭ࡥࡵࡕࡨࡷࡸ࡯࡯࡯ࡆࡨࡸࡦ࡯࡬ࡴࠤࢀࡠࠬ࠯ࠩࠪ࡝ࠥ࡬ࡦࡹࡨࡦࡦࡢ࡭ࡩࠨ࡝ࠪࠢ࠮ࠤࠧ࠲࡜࡝ࡰࠥ࠭ࡡࡴࠠࠡࠢࠣࢁࡨࡧࡴࡤࡪࠫࡩࡽ࠯ࡻ࡝ࡰࠣࠤࠥࠦࡽ࡝ࡰࠣࠤࢂࡢ࡮ࠡࠢ࠲࠮ࠥࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾ࠢ࠭࠳ࠬ੷")
bstack1ll1llll1_opy_ = bstack1llllll11_opy_ (u"࠭࡜࡯࠱࠭ࠤࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽ࠡࠬ࠲ࡠࡳࡩ࡯࡯ࡵࡷࠤࡧࡹࡴࡢࡥ࡮ࡣࡵࡧࡴࡩࠢࡀࠤࡵࡸ࡯ࡤࡧࡶࡷ࠳ࡧࡲࡨࡸ࡞ࡴࡷࡵࡣࡦࡵࡶ࠲ࡦࡸࡧࡷ࠰࡯ࡩࡳ࡭ࡴࡩࠢ࠰ࠤ࠸ࡣ࡜࡯ࡥࡲࡲࡸࡺࠠࡣࡵࡷࡥࡨࡱ࡟ࡤࡣࡳࡷࠥࡃࠠࡱࡴࡲࡧࡪࡹࡳ࠯ࡣࡵ࡫ࡻࡡࡰࡳࡱࡦࡩࡸࡹ࠮ࡢࡴࡪࡺ࠳ࡲࡥ࡯ࡩࡷ࡬ࠥ࠳ࠠ࠲࡟࡟ࡲࡨࡵ࡮ࡴࡶࠣࡴࡤ࡯࡮ࡥࡧࡻࠤࡂࠦࡰࡳࡱࡦࡩࡸࡹ࠮ࡢࡴࡪࡺࡠࡶࡲࡰࡥࡨࡷࡸ࠴ࡡࡳࡩࡹ࠲ࡱ࡫࡮ࡨࡶ࡫ࠤ࠲ࠦ࠲࡞࡞ࡱࡴࡷࡵࡣࡦࡵࡶ࠲ࡦࡸࡧࡷࠢࡀࠤࡵࡸ࡯ࡤࡧࡶࡷ࠳ࡧࡲࡨࡸ࠱ࡷࡱ࡯ࡣࡦࠪ࠳࠰ࠥࡶࡲࡰࡥࡨࡷࡸ࠴ࡡࡳࡩࡹ࠲ࡱ࡫࡮ࡨࡶ࡫ࠤ࠲ࠦ࠳ࠪ࡞ࡱࡧࡴࡴࡳࡵࠢ࡬ࡱࡵࡵࡲࡵࡡࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹ࠺࡟ࡣࡵࡷࡥࡨࡱࠠ࠾ࠢࡵࡩࡶࡻࡩࡳࡧࠫࠦࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࠣࠫ࠾ࡠࡳ࡯࡭ࡱࡱࡵࡸࡤࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵ࠶ࡢࡦࡸࡺࡡࡤ࡭࠱ࡧ࡭ࡸ࡯࡮࡫ࡸࡱ࠳ࡲࡡࡶࡰࡦ࡬ࠥࡃࠠࡢࡵࡼࡲࡨࠦࠨ࡭ࡣࡸࡲࡨ࡮ࡏࡱࡶ࡬ࡳࡳࡹࠩࠡ࠿ࡁࠤࢀࡢ࡮࡭ࡧࡷࠤࡨࡧࡰࡴ࠽࡟ࡲࡹࡸࡹࠡࡽ࡟ࡲࡨࡧࡰࡴࠢࡀࠤࡏ࡙ࡏࡏ࠰ࡳࡥࡷࡹࡥࠩࡤࡶࡸࡦࡩ࡫ࡠࡥࡤࡴࡸ࠯࡜࡯ࠢࠣࢁࠥࡩࡡࡵࡥ࡫ࠬࡪࡾࠩࠡࡽ࡟ࡲࠥࠦࠠࠡࡿ࡟ࡲࠥࠦࡲࡦࡶࡸࡶࡳࠦࡡࡸࡣ࡬ࡸࠥ࡯࡭ࡱࡱࡵࡸࡤࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵ࠶ࡢࡦࡸࡺࡡࡤ࡭࠱ࡧ࡭ࡸ࡯࡮࡫ࡸࡱ࠳ࡩ࡯࡯ࡰࡨࡧࡹ࠮ࡻ࡝ࡰࠣࠤࠥࠦࡷࡴࡇࡱࡨࡵࡵࡩ࡯ࡶ࠽ࠤࡥࡽࡳࡴ࠼࠲࠳ࡨࡪࡰ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡱࡰ࠳ࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࡀࡥࡤࡴࡸࡃࠤࡼࡧࡱࡧࡴࡪࡥࡖࡔࡌࡇࡴࡳࡰࡰࡰࡨࡲࡹ࠮ࡊࡔࡑࡑ࠲ࡸࡺࡲࡪࡰࡪ࡭࡫ࡿࠨࡤࡣࡳࡷ࠮࠯ࡽࡡ࠮࡟ࡲࠥࠦࠠࠡ࠰࠱࠲ࡱࡧࡵ࡯ࡥ࡫ࡓࡵࡺࡩࡰࡰࡶࡠࡳࠦࠠࡾࠫ࡟ࡲࢂࡢ࡮࠰ࠬࠣࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃࠠࠫ࠱࡟ࡲࠬ੸")
from ._version import __version__
bstack11111111_opy_ = None
CONFIG = {}
bstack11l1_opy_ = {}
bstack1l111l11l_opy_ = {}
bstack1ll11l11_opy_ = None
bstack111l111l_opy_ = None
bstack1l1ll1ll_opy_ = None
bstack1111lll1l_opy_ = -1
bstack11l11llll_opy_ = bstack111llll1_opy_
bstack1ll11l111_opy_ = 1
bstack11l11lll1_opy_ = False
bstack1l11l1111_opy_ = False
bstack1l1l1l_opy_ = bstack1llllll11_opy_ (u"ࠧࠨ੹")
bstack11111l11_opy_ = bstack1llllll11_opy_ (u"ࠨࠩ੺")
bstack111ll1ll1_opy_ = False
bstack1llll1ll1_opy_ = True
bstack1l1l1l11l_opy_ = bstack1llllll11_opy_ (u"ࠩࠪ੻")
bstack1lll1ll1l_opy_ = []
bstack1l1111ll1_opy_ = bstack1llllll11_opy_ (u"ࠪࠫ੼")
bstack1l111111l_opy_ = False
bstack11l111l_opy_ = None
bstack111_opy_ = None
bstack11l1l11_opy_ = -1
bstack1l1lll_opy_ = os.path.join(os.path.expanduser(bstack1llllll11_opy_ (u"ࠫࢃ࠭੽")), bstack1llllll11_opy_ (u"ࠬ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠬ੾"), bstack1llllll11_opy_ (u"࠭࠮ࡳࡱࡥࡳࡹ࠳ࡲࡦࡲࡲࡶࡹ࠳ࡨࡦ࡮ࡳࡩࡷ࠴ࡪࡴࡱࡱࠫ੿"))
bstack11l11l11l_opy_ = []
bstack1llll1l11_opy_ = False
bstack1ll1lll1l_opy_ = False
bstack1llll1l_opy_ = None
bstack1ll11ll_opy_ = None
bstack11111_opy_ = None
bstack1l111l111_opy_ = None
bstack11l111l11_opy_ = None
bstack11l1ll1l1_opy_ = None
bstack11_opy_ = None
bstack1l111l1l_opy_ = None
bstack11llllll1_opy_ = None
bstack11l1l111_opy_ = None
bstack11l1ll1_opy_ = None
bstack111l1111_opy_ = None
bstack1llll1l1_opy_ = None
bstack11ll1l1_opy_ = None
bstack1ll11l1_opy_ = None
bstack11ll11l1l_opy_ = None
bstack11lllll11_opy_ = None
bstack1llll11ll_opy_ = None
bstack11ll11l_opy_ = bstack1llllll11_opy_ (u"ࠢࠣ઀")
class bstack1l1lll111_opy_(threading.Thread):
  def run(self):
    self.exc = None
    try:
      self.ret = self._target(*self._args, **self._kwargs)
    except Exception as e:
      self.exc = e
  def join(self, timeout=None):
    super(bstack1l1lll111_opy_, self).join(timeout)
    if self.exc:
      raise self.exc
    return self.ret
logger = logging.getLogger(__name__)
logging.basicConfig(level=bstack11l11llll_opy_,
                    format=bstack1llllll11_opy_ (u"ࠨ࡞ࡱࠩ࠭ࡧࡳࡤࡶ࡬ࡱࡪ࠯ࡳࠡ࡝ࠨࠬࡳࡧ࡭ࡦࠫࡶࡡࡠࠫࠨ࡭ࡧࡹࡩࡱࡴࡡ࡮ࡧࠬࡷࡢࠦ࠭ࠡࠧࠫࡱࡪࡹࡳࡢࡩࡨ࠭ࡸ࠭ઁ"),
                    datefmt=bstack1llllll11_opy_ (u"ࠩࠨࡌ࠿ࠫࡍ࠻ࠧࡖࠫં"))
def bstack11l1l1ll1_opy_():
  global CONFIG
  global bstack11l11llll_opy_
  if bstack1llllll11_opy_ (u"ࠪࡰࡴ࡭ࡌࡦࡸࡨࡰࠬઃ") in CONFIG:
    bstack11l11llll_opy_ = bstack11ll1llll_opy_[CONFIG[bstack1llllll11_opy_ (u"ࠫࡱࡵࡧࡍࡧࡹࡩࡱ࠭઄")]]
    logging.getLogger().setLevel(bstack11l11llll_opy_)
def bstack11ll1ll11_opy_():
  global CONFIG
  global bstack1llll1l11_opy_
  bstack1ll1l11l_opy_ = bstack11l1l1l1_opy_(CONFIG)
  if(bstack1llllll11_opy_ (u"ࠬࡹ࡫ࡪࡲࡖࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧઅ") in bstack1ll1l11l_opy_ and str(bstack1ll1l11l_opy_[bstack1llllll11_opy_ (u"࠭ࡳ࡬࡫ࡳࡗࡪࡹࡳࡪࡱࡱࡒࡦࡳࡥࠨઆ")]).lower() == bstack1llllll11_opy_ (u"ࠧࡵࡴࡸࡩࠬઇ")):
    bstack1llll1l11_opy_ = True
def bstack111ll11ll_opy_():
  from appium.version import version as appium_version
  return version.parse(appium_version)
def bstack1l11l111l_opy_():
  from selenium import webdriver
  return version.parse(webdriver.__version__)
def bstack1l1lll11_opy_():
  args = sys.argv
  for i in range(len(args)):
    if bstack1llllll11_opy_ (u"ࠣ࠯࠰ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡥࡲࡲ࡫࡯ࡧࡧ࡫࡯ࡩࠧઈ") == args[i].lower() or bstack1llllll11_opy_ (u"ࠤ࠰࠱ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡧࡴࡴࡦࡪࡩࠥઉ") == args[i].lower():
      path = args[i+1]
      sys.argv.remove(args[i])
      sys.argv.remove(path)
      global bstack1l1l1l11l_opy_
      bstack1l1l1l11l_opy_ += bstack1llllll11_opy_ (u"ࠪ࠱࠲ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡇࡴࡴࡦࡪࡩࡉ࡭ࡱ࡫ࠠࠨઊ") + path
      return path
  return None
bstack1lll11111_opy_ = re.compile(bstack1llllll11_opy_ (u"ࡶࠧ࠴ࠪࡀ࡞ࠧࡿ࠭࠴ࠪࡀࠫࢀ࠲࠯ࡅࠢઋ"))
def bstack11l1lll1_opy_(loader, node):
    value = loader.construct_scalar(node)
    for group in bstack1lll11111_opy_.findall(value):
        if group is not None and os.environ.get(group) is not None:
          value = value.replace(bstack1llllll11_opy_ (u"ࠧࠪࡻࠣઌ") + group + bstack1llllll11_opy_ (u"ࠨࡽࠣઍ"), os.environ.get(group))
    return value
def bstack1111l11_opy_():
  bstack111llll1l_opy_ = bstack1l1lll11_opy_()
  if bstack111llll1l_opy_ and os.path.exists(os.path.abspath(bstack111llll1l_opy_)):
    fileName = bstack111llll1l_opy_
  if bstack1llllll11_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡃࡐࡐࡉࡍࡌࡥࡆࡊࡎࡈࠫ઎") in os.environ and os.path.exists(os.path.abspath(os.environ[bstack1llllll11_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡄࡑࡑࡊࡎࡍ࡟ࡇࡋࡏࡉࠬએ")])) and not bstack1llllll11_opy_ (u"ࠩࡩ࡭ࡱ࡫ࡎࡢ࡯ࡨࠫઐ") in locals():
    fileName = os.environ[bstack1llllll11_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡆࡓࡓࡌࡉࡈࡡࡉࡍࡑࡋࠧઑ")]
  if bstack1llllll11_opy_ (u"ࠫ࡫࡯࡬ࡦࡐࡤࡱࡪ࠭઒") in locals():
    bstack11l1ll11_opy_ = os.path.abspath(fileName)
  else:
    bstack11l1ll11_opy_ = bstack1llllll11_opy_ (u"ࠬ࠭ઓ")
  bstack1l11ll1_opy_ = os.getcwd()
  bstack111ll1_opy_ = bstack1llllll11_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡿ࡭࡭ࠩઔ")
  bstack1l11ll11l_opy_ = bstack1llllll11_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡹࡢ࡯࡯ࠫક")
  while (not os.path.exists(bstack11l1ll11_opy_)) and bstack1l11ll1_opy_ != bstack1llllll11_opy_ (u"ࠣࠤખ"):
    bstack11l1ll11_opy_ = os.path.join(bstack1l11ll1_opy_, bstack111ll1_opy_)
    if not os.path.exists(bstack11l1ll11_opy_):
      bstack11l1ll11_opy_ = os.path.join(bstack1l11ll1_opy_, bstack1l11ll11l_opy_)
    if bstack1l11ll1_opy_ != os.path.dirname(bstack1l11ll1_opy_):
      bstack1l11ll1_opy_ = os.path.dirname(bstack1l11ll1_opy_)
    else:
      bstack1l11ll1_opy_ = bstack1llllll11_opy_ (u"ࠤࠥગ")
  if not os.path.exists(bstack11l1ll11_opy_):
    bstack1l1lll1_opy_(
      bstack111l1ll1_opy_.format(os.getcwd()))
  try:
    with open(bstack11l1ll11_opy_, bstack1llllll11_opy_ (u"ࠪࡶࠬઘ")) as stream:
        yaml.add_implicit_resolver(bstack1llllll11_opy_ (u"ࠦࠦࡶࡡࡵࡪࡨࡼࠧઙ"), bstack1lll11111_opy_)
        yaml.add_constructor(bstack1llllll11_opy_ (u"ࠧࠧࡰࡢࡶ࡫ࡩࡽࠨચ"), bstack11l1lll1_opy_)
        config = yaml.load(stream, yaml.FullLoader)
        return config
  except:
    with open(bstack11l1ll11_opy_, bstack1llllll11_opy_ (u"࠭ࡲࠨછ")) as stream:
      try:
        config = yaml.safe_load(stream)
        return config
      except yaml.YAMLError as exc:
        bstack1l1lll1_opy_(bstack1l11l1l1_opy_.format(str(exc)))
def bstack111l11l11_opy_(config):
  bstack111ll1l_opy_ = bstack1l11l1l11_opy_(config)
  for option in list(bstack111ll1l_opy_):
    if option.lower() in bstack111l111ll_opy_ and option != bstack111l111ll_opy_[option.lower()]:
      bstack111ll1l_opy_[bstack111l111ll_opy_[option.lower()]] = bstack111ll1l_opy_[option]
      del bstack111ll1l_opy_[option]
  return config
def bstack1ll1ll11l_opy_():
  global bstack1l111l11l_opy_
  for key, bstack11llll1l1_opy_ in bstack11lll11l1_opy_.items():
    if isinstance(bstack11llll1l1_opy_, list):
      for var in bstack11llll1l1_opy_:
        if var in os.environ and os.environ[var] and str(os.environ[var]).strip():
          bstack1l111l11l_opy_[key] = os.environ[var]
          break
    elif bstack11llll1l1_opy_ in os.environ and os.environ[bstack11llll1l1_opy_] and str(os.environ[bstack11llll1l1_opy_]).strip():
      bstack1l111l11l_opy_[key] = os.environ[bstack11llll1l1_opy_]
  if bstack1llllll11_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡌࡐࡅࡄࡐࡤࡏࡄࡆࡐࡗࡍࡋࡏࡅࡓࠩજ") in os.environ:
    bstack1l111l11l_opy_[bstack1llllll11_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࡌࡰࡥࡤࡰࡔࡶࡴࡪࡱࡱࡷࠬઝ")] = {}
    bstack1l111l11l_opy_[bstack1llllll11_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡍࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭ઞ")][bstack1llllll11_opy_ (u"ࠪࡰࡴࡩࡡ࡭ࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬટ")] = os.environ[bstack1llllll11_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡐࡔࡉࡁࡍࡡࡌࡈࡊࡔࡔࡊࡈࡌࡉࡗ࠭ઠ")]
def bstack11ll1111_opy_():
  global bstack11l1_opy_
  global bstack1l1l1l11l_opy_
  for idx, val in enumerate(sys.argv):
    if idx<len(sys.argv) and bstack1llllll11_opy_ (u"ࠬ࠳࠭ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴࡬ࡰࡥࡤࡰࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨડ").lower() == val.lower():
      bstack11l1_opy_[bstack1llllll11_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪઢ")] = {}
      bstack11l1_opy_[bstack1llllll11_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࡓࡵࡺࡩࡰࡰࡶࠫણ")][bstack1llllll11_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪત")] = sys.argv[idx+1]
      del sys.argv[idx:idx+2]
      break
  for key, bstack1lll1l_opy_ in bstack11ll111l1_opy_.items():
    if isinstance(bstack1lll1l_opy_, list):
      for idx, val in enumerate(sys.argv):
        for var in bstack1lll1l_opy_:
          if idx<len(sys.argv) and bstack1llllll11_opy_ (u"ࠩ࠰࠱ࠬથ") + var.lower() == val.lower() and not key in bstack11l1_opy_:
            bstack11l1_opy_[key] = sys.argv[idx+1]
            bstack1l1l1l11l_opy_ += bstack1llllll11_opy_ (u"ࠪࠤ࠲࠳ࠧદ") + var + bstack1llllll11_opy_ (u"ࠫࠥ࠭ધ") + sys.argv[idx+1]
            del sys.argv[idx:idx+2]
            break
    else:
      for idx, val in enumerate(sys.argv):
        if idx<len(sys.argv) and bstack1llllll11_opy_ (u"ࠬ࠳࠭ࠨન") + bstack1lll1l_opy_.lower() == val.lower() and not key in bstack11l1_opy_:
          bstack11l1_opy_[key] = sys.argv[idx+1]
          bstack1l1l1l11l_opy_ += bstack1llllll11_opy_ (u"࠭ࠠ࠮࠯ࠪ઩") + bstack1lll1l_opy_ + bstack1llllll11_opy_ (u"ࠧࠡࠩપ") + sys.argv[idx+1]
          del sys.argv[idx:idx+2]
def bstack11lll111l_opy_(config):
  bstack11l_opy_ = config.keys()
  for bstack1l1l_opy_, bstack1lll1l1ll_opy_ in bstack111l11l1_opy_.items():
    if bstack1lll1l1ll_opy_ in bstack11l_opy_:
      config[bstack1l1l_opy_] = config[bstack1lll1l1ll_opy_]
      del config[bstack1lll1l1ll_opy_]
  for bstack1l1l_opy_, bstack1lll1l1ll_opy_ in bstack1l1l1l1ll_opy_.items():
    if isinstance(bstack1lll1l1ll_opy_, list):
      for bstack1l1ll11l_opy_ in bstack1lll1l1ll_opy_:
        if bstack1l1ll11l_opy_ in bstack11l_opy_:
          config[bstack1l1l_opy_] = config[bstack1l1ll11l_opy_]
          del config[bstack1l1ll11l_opy_]
          break
    elif bstack1lll1l1ll_opy_ in bstack11l_opy_:
        config[bstack1l1l_opy_] = config[bstack1lll1l1ll_opy_]
        del config[bstack1lll1l1ll_opy_]
  for bstack1l1ll11l_opy_ in list(config):
    for bstack1111ll11_opy_ in bstack1llll11l_opy_:
      if bstack1l1ll11l_opy_.lower() == bstack1111ll11_opy_.lower() and bstack1l1ll11l_opy_ != bstack1111ll11_opy_:
        config[bstack1111ll11_opy_] = config[bstack1l1ll11l_opy_]
        del config[bstack1l1ll11l_opy_]
  bstack1ll11lll1_opy_ = []
  if bstack1llllll11_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫફ") in config:
    bstack1ll11lll1_opy_ = config[bstack1llllll11_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬબ")]
  for platform in bstack1ll11lll1_opy_:
    for bstack1l1ll11l_opy_ in list(platform):
      for bstack1111ll11_opy_ in bstack1llll11l_opy_:
        if bstack1l1ll11l_opy_.lower() == bstack1111ll11_opy_.lower() and bstack1l1ll11l_opy_ != bstack1111ll11_opy_:
          platform[bstack1111ll11_opy_] = platform[bstack1l1ll11l_opy_]
          del platform[bstack1l1ll11l_opy_]
  for bstack1l1l_opy_, bstack1lll1l1ll_opy_ in bstack1l1l1l1ll_opy_.items():
    for platform in bstack1ll11lll1_opy_:
      if isinstance(bstack1lll1l1ll_opy_, list):
        for bstack1l1ll11l_opy_ in bstack1lll1l1ll_opy_:
          if bstack1l1ll11l_opy_ in platform:
            platform[bstack1l1l_opy_] = platform[bstack1l1ll11l_opy_]
            del platform[bstack1l1ll11l_opy_]
            break
      elif bstack1lll1l1ll_opy_ in platform:
        platform[bstack1l1l_opy_] = platform[bstack1lll1l1ll_opy_]
        del platform[bstack1lll1l1ll_opy_]
  for bstack11l11l1l_opy_ in bstack11lll1l1l_opy_:
    if bstack11l11l1l_opy_ in config:
      if not bstack11lll1l1l_opy_[bstack11l11l1l_opy_] in config:
        config[bstack11lll1l1l_opy_[bstack11l11l1l_opy_]] = {}
      config[bstack11lll1l1l_opy_[bstack11l11l1l_opy_]].update(config[bstack11l11l1l_opy_])
      del config[bstack11l11l1l_opy_]
  for platform in bstack1ll11lll1_opy_:
    for bstack11l11l1l_opy_ in bstack11lll1l1l_opy_:
      if bstack11l11l1l_opy_ in list(platform):
        if not bstack11lll1l1l_opy_[bstack11l11l1l_opy_] in platform:
          platform[bstack11lll1l1l_opy_[bstack11l11l1l_opy_]] = {}
        platform[bstack11lll1l1l_opy_[bstack11l11l1l_opy_]].update(platform[bstack11l11l1l_opy_])
        del platform[bstack11l11l1l_opy_]
  config = bstack111l11l11_opy_(config)
  return config
def bstack1l1lll11l_opy_(config):
  global bstack11111l11_opy_
  if bstack1llllll11_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࠧભ") in config and str(config[bstack1llllll11_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࠨમ")]).lower() != bstack1llllll11_opy_ (u"ࠬ࡬ࡡ࡭ࡵࡨࠫય"):
    if not bstack1llllll11_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪર") in config:
      config[bstack1llllll11_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࡓࡵࡺࡩࡰࡰࡶࠫ઱")] = {}
    if not bstack1llllll11_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪલ") in config[bstack1llllll11_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡍࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭ળ")]:
      bstack11ll11ll1_opy_ = datetime.datetime.now()
      bstack111llll11_opy_ = bstack11ll11ll1_opy_.strftime(bstack1llllll11_opy_ (u"ࠪࠩࡩࡥࠥࡣࡡࠨࡌࠪࡓࠧ઴"))
      hostname = socket.gethostname()
      bstack11l11l111_opy_ = bstack1llllll11_opy_ (u"ࠫࠬવ").join(random.choices(string.ascii_lowercase + string.digits, k=4))
      identifier = bstack1llllll11_opy_ (u"ࠬࢁࡽࡠࡽࢀࡣࢀࢃࠧશ").format(bstack111llll11_opy_, hostname, bstack11l11l111_opy_)
      config[bstack1llllll11_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪષ")][bstack1llllll11_opy_ (u"ࠧ࡭ࡱࡦࡥࡱࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩસ")] = identifier
    bstack11111l11_opy_ = config[bstack1llllll11_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࡌࡰࡥࡤࡰࡔࡶࡴࡪࡱࡱࡷࠬહ")][bstack1llllll11_opy_ (u"ࠩ࡯ࡳࡨࡧ࡬ࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫ઺")]
  return config
def bstack1l1lll1l_opy_():
  if (
    isinstance(os.getenv(bstack1llllll11_opy_ (u"ࠪࡎࡊࡔࡋࡊࡐࡖࡣ࡚ࡘࡌࠨ઻")), str) and len(os.getenv(bstack1llllll11_opy_ (u"ࠫࡏࡋࡎࡌࡋࡑࡗࡤ࡛ࡒࡍ઼ࠩ"))) > 0
  ) or (
    isinstance(os.getenv(bstack1llllll11_opy_ (u"ࠬࡐࡅࡏࡍࡌࡒࡘࡥࡈࡐࡏࡈࠫઽ")), str) and len(os.getenv(bstack1llllll11_opy_ (u"࠭ࡊࡆࡐࡎࡍࡓ࡙࡟ࡉࡑࡐࡉࠬા"))) > 0
  ):
    return os.getenv(bstack1llllll11_opy_ (u"ࠧࡃࡗࡌࡐࡉࡥࡎࡖࡏࡅࡉࡗ࠭િ"), 0)
  if str(os.getenv(bstack1llllll11_opy_ (u"ࠨࡅࡌࠫી"))).lower() == bstack1llllll11_opy_ (u"ࠩࡷࡶࡺ࡫ࠧુ") and str(os.getenv(bstack1llllll11_opy_ (u"ࠪࡇࡎࡘࡃࡍࡇࡆࡍࠬૂ"))).lower() == bstack1llllll11_opy_ (u"ࠫࡹࡸࡵࡦࠩૃ"):
    return os.getenv(bstack1llllll11_opy_ (u"ࠬࡉࡉࡓࡅࡏࡉࡤࡈࡕࡊࡎࡇࡣࡓ࡛ࡍࠨૄ"), 0)
  if str(os.getenv(bstack1llllll11_opy_ (u"࠭ࡃࡊࠩૅ"))).lower() == bstack1llllll11_opy_ (u"ࠧࡵࡴࡸࡩࠬ૆") and str(os.getenv(bstack1llllll11_opy_ (u"ࠨࡖࡕࡅ࡛ࡏࡓࠨે"))).lower() == bstack1llllll11_opy_ (u"ࠩࡷࡶࡺ࡫ࠧૈ"):
    return os.getenv(bstack1llllll11_opy_ (u"ࠪࡘࡗࡇࡖࡊࡕࡢࡆ࡚ࡏࡌࡅࡡࡑ࡙ࡒࡈࡅࡓࠩૉ"), 0)
  if str(os.getenv(bstack1llllll11_opy_ (u"ࠫࡈࡏࠧ૊"))).lower() == bstack1llllll11_opy_ (u"ࠬࡺࡲࡶࡧࠪો") and str(os.getenv(bstack1llllll11_opy_ (u"࠭ࡃࡊࡡࡑࡅࡒࡋࠧૌ"))).lower() == bstack1llllll11_opy_ (u"ࠧࡤࡱࡧࡩࡸ࡮ࡩࡱ્ࠩ"):
    return 0 # bstack111ll1ll_opy_ bstack1lll11_opy_ not set build number env
  if os.getenv(bstack1llllll11_opy_ (u"ࠨࡄࡌࡘࡇ࡛ࡃࡌࡇࡗࡣࡇࡘࡁࡏࡅࡋࠫ૎")) and os.getenv(bstack1llllll11_opy_ (u"ࠩࡅࡍ࡙ࡈࡕࡄࡍࡈࡘࡤࡉࡏࡎࡏࡌࡘࠬ૏")):
    return os.getenv(bstack1llllll11_opy_ (u"ࠪࡆࡎ࡚ࡂࡖࡅࡎࡉ࡙ࡥࡂࡖࡋࡏࡈࡤࡔࡕࡎࡄࡈࡖࠬૐ"), 0)
  if str(os.getenv(bstack1llllll11_opy_ (u"ࠫࡈࡏࠧ૑"))).lower() == bstack1llllll11_opy_ (u"ࠬࡺࡲࡶࡧࠪ૒") and str(os.getenv(bstack1llllll11_opy_ (u"࠭ࡄࡓࡑࡑࡉࠬ૓"))).lower() == bstack1llllll11_opy_ (u"ࠧࡵࡴࡸࡩࠬ૔"):
    return os.getenv(bstack1llllll11_opy_ (u"ࠨࡆࡕࡓࡓࡋ࡟ࡃࡗࡌࡐࡉࡥࡎࡖࡏࡅࡉࡗ࠭૕"), 0)
  if str(os.getenv(bstack1llllll11_opy_ (u"ࠩࡆࡍࠬ૖"))).lower() == bstack1llllll11_opy_ (u"ࠪࡸࡷࡻࡥࠨ૗") and str(os.getenv(bstack1llllll11_opy_ (u"ࠫࡘࡋࡍࡂࡒࡋࡓࡗࡋࠧ૘"))).lower() == bstack1llllll11_opy_ (u"ࠬࡺࡲࡶࡧࠪ૙"):
    return os.getenv(bstack1llllll11_opy_ (u"࠭ࡓࡆࡏࡄࡔࡍࡕࡒࡆࡡࡍࡓࡇࡥࡉࡅࠩ૚"), 0)
  if str(os.getenv(bstack1llllll11_opy_ (u"ࠧࡄࡋࠪ૛"))).lower() == bstack1llllll11_opy_ (u"ࠨࡶࡵࡹࡪ࠭૜") and str(os.getenv(bstack1llllll11_opy_ (u"ࠩࡊࡍ࡙ࡒࡁࡃࡡࡆࡍࠬ૝"))).lower() == bstack1llllll11_opy_ (u"ࠪࡸࡷࡻࡥࠨ૞"):
    return os.getenv(bstack1llllll11_opy_ (u"ࠫࡈࡏ࡟ࡋࡑࡅࡣࡎࡊࠧ૟"), 0)
  if str(os.getenv(bstack1llllll11_opy_ (u"ࠬࡉࡉࠨૠ"))).lower() == bstack1llllll11_opy_ (u"࠭ࡴࡳࡷࡨࠫૡ") and str(os.getenv(bstack1llllll11_opy_ (u"ࠧࡃࡗࡌࡐࡉࡑࡉࡕࡇࠪૢ"))).lower() == bstack1llllll11_opy_ (u"ࠨࡶࡵࡹࡪ࠭ૣ"):
    return os.getenv(bstack1llllll11_opy_ (u"ࠩࡅ࡙ࡎࡒࡄࡌࡋࡗࡉࡤࡈࡕࡊࡎࡇࡣࡓ࡛ࡍࡃࡇࡕࠫ૤"), 0)
  if str(os.getenv(bstack1llllll11_opy_ (u"ࠪࡘࡋࡥࡂࡖࡋࡏࡈࠬ૥"))).lower() == bstack1llllll11_opy_ (u"ࠫࡹࡸࡵࡦࠩ૦"):
    return os.getenv(bstack1llllll11_opy_ (u"ࠬࡈࡕࡊࡎࡇࡣࡇ࡛ࡉࡍࡆࡌࡈࠬ૧"), 0)
  return -1
def bstack111l11l_opy_(bstack1ll1l_opy_):
  global CONFIG
  if not bstack1llllll11_opy_ (u"࠭ࠤࡼࡄࡘࡍࡑࡊ࡟ࡏࡗࡐࡆࡊࡘࡽࠨ૨") in CONFIG[bstack1llllll11_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩ૩")]:
    return
  CONFIG[bstack1llllll11_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪ૪")] = CONFIG[bstack1llllll11_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫ૫")].replace(
    bstack1llllll11_opy_ (u"ࠪࠨࢀࡈࡕࡊࡎࡇࡣࡓ࡛ࡍࡃࡇࡕࢁࠬ૬"),
    str(bstack1ll1l_opy_)
  )
def bstack1l1l111ll_opy_():
  global CONFIG
  if not bstack1llllll11_opy_ (u"ࠫࠩࢁࡄࡂࡖࡈࡣ࡙ࡏࡍࡆࡿࠪ૭") in CONFIG[bstack1llllll11_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧ૮")]:
    return
  bstack11ll11ll1_opy_ = datetime.datetime.now()
  bstack111llll11_opy_ = bstack11ll11ll1_opy_.strftime(bstack1llllll11_opy_ (u"࠭ࠥࡥ࠯ࠨࡦ࠲ࠫࡈ࠻ࠧࡐࠫ૯"))
  CONFIG[bstack1llllll11_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩ૰")] = CONFIG[bstack1llllll11_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪ૱")].replace(
    bstack1llllll11_opy_ (u"ࠩࠧࡿࡉࡇࡔࡆࡡࡗࡍࡒࡋࡽࠨ૲"),
    bstack111llll11_opy_
  )
def bstack111ll1lll_opy_():
  global CONFIG
  if bstack1llllll11_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬ૳") in CONFIG and not bool(CONFIG[bstack1llllll11_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭૴")]):
    del CONFIG[bstack1llllll11_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧ૵")]
    return
  if not bstack1llllll11_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨ૶") in CONFIG:
    CONFIG[bstack1llllll11_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩ૷")] = bstack1llllll11_opy_ (u"ࠨࠥࠧࡿࡇ࡛ࡉࡍࡆࡢࡒ࡚ࡓࡂࡆࡔࢀࠫ૸")
  if bstack1llllll11_opy_ (u"ࠩࠧࡿࡉࡇࡔࡆࡡࡗࡍࡒࡋࡽࠨૹ") in CONFIG[bstack1llllll11_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬૺ")]:
    bstack1l1l111ll_opy_()
    os.environ[bstack1llllll11_opy_ (u"ࠫࡇ࡙ࡔࡂࡅࡎࡣࡈࡕࡍࡃࡋࡑࡉࡉࡥࡂࡖࡋࡏࡈࡤࡏࡄࠨૻ")] = CONFIG[bstack1llllll11_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧૼ")]
  if not bstack1llllll11_opy_ (u"࠭ࠤࡼࡄࡘࡍࡑࡊ࡟ࡏࡗࡐࡆࡊࡘࡽࠨ૽") in CONFIG[bstack1llllll11_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩ૾")]:
    return
  bstack1ll1l_opy_ = bstack1llllll11_opy_ (u"ࠨࠩ૿")
  bstack111lllll_opy_ = bstack1l1lll1l_opy_()
  if bstack111lllll_opy_ != -1:
    bstack1ll1l_opy_ = bstack1llllll11_opy_ (u"ࠩࡆࡍࠥ࠭଀") + str(bstack111lllll_opy_)
  if bstack1ll1l_opy_ == bstack1llllll11_opy_ (u"ࠪࠫଁ"):
    bstack11ll1lll_opy_ = bstack11ll1l11_opy_(CONFIG[bstack1llllll11_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠧଂ")])
    if bstack11ll1lll_opy_ != -1:
      bstack1ll1l_opy_ = str(bstack11ll1lll_opy_)
  if bstack1ll1l_opy_:
    bstack111l11l_opy_(bstack1ll1l_opy_)
    os.environ[bstack1llllll11_opy_ (u"ࠬࡈࡓࡕࡃࡆࡏࡤࡉࡏࡎࡄࡌࡒࡊࡊ࡟ࡃࡗࡌࡐࡉࡥࡉࡅࠩଃ")] = CONFIG[bstack1llllll11_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨ଄")]
def bstack1l1l1l11_opy_(bstack111ll11l1_opy_, bstack1l1ll111_opy_, path):
  bstack1l1l111_opy_ = {
    bstack1llllll11_opy_ (u"ࠧࡪࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫଅ"): bstack1l1ll111_opy_
  }
  if os.path.exists(path):
    bstack11ll1lll1_opy_ = json.load(open(path, bstack1llllll11_opy_ (u"ࠨࡴࡥࠫଆ")))
  else:
    bstack11ll1lll1_opy_ = {}
  bstack11ll1lll1_opy_[bstack111ll11l1_opy_] = bstack1l1l111_opy_
  with open(path, bstack1llllll11_opy_ (u"ࠤࡺ࠯ࠧଇ")) as outfile:
    json.dump(bstack11ll1lll1_opy_, outfile)
def bstack11ll1l11_opy_(bstack111ll11l1_opy_):
  bstack111ll11l1_opy_ = str(bstack111ll11l1_opy_)
  bstack1ll1lllll_opy_ = os.path.join(os.path.expanduser(bstack1llllll11_opy_ (u"ࠪࢂࠬଈ")), bstack1llllll11_opy_ (u"ࠫ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠫଉ"))
  try:
    if not os.path.exists(bstack1ll1lllll_opy_):
      os.makedirs(bstack1ll1lllll_opy_)
    file_path = os.path.join(os.path.expanduser(bstack1llllll11_opy_ (u"ࠬࢄࠧଊ")), bstack1llllll11_opy_ (u"࠭࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠭ଋ"), bstack1llllll11_opy_ (u"ࠧ࠯ࡤࡸ࡭ࡱࡪ࠭࡯ࡣࡰࡩ࠲ࡩࡡࡤࡪࡨ࠲࡯ࡹ࡯࡯ࠩଌ"))
    if not os.path.isfile(file_path):
      with open(file_path, bstack1llllll11_opy_ (u"ࠨࡹࠪ଍")):
        pass
      with open(file_path, bstack1llllll11_opy_ (u"ࠤࡺ࠯ࠧ଎")) as outfile:
        json.dump({}, outfile)
    with open(file_path, bstack1llllll11_opy_ (u"ࠪࡶࠬଏ")) as bstack1llll11_opy_:
      bstack1l1ll11ll_opy_ = json.load(bstack1llll11_opy_)
    if bstack111ll11l1_opy_ in bstack1l1ll11ll_opy_:
      bstack1lll11ll1_opy_ = bstack1l1ll11ll_opy_[bstack111ll11l1_opy_][bstack1llllll11_opy_ (u"ࠫ࡮ࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨଐ")]
      bstack1l111_opy_ = int(bstack1lll11ll1_opy_) + 1
      bstack1l1l1l11_opy_(bstack111ll11l1_opy_, bstack1l111_opy_, file_path)
      return bstack1l111_opy_
    else:
      bstack1l1l1l11_opy_(bstack111ll11l1_opy_, 1, file_path)
      return 1
  except Exception as e:
    logger.warn(bstack1l1111l11_opy_.format(str(e)))
    return -1
def bstack111ll1l1_opy_(config):
  if not config[bstack1llllll11_opy_ (u"ࠬࡻࡳࡦࡴࡑࡥࡲ࡫ࠧ଑")] or not config[bstack1llllll11_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸࡑࡥࡺࠩ଒")]:
    return True
  else:
    return False
def bstack11ll_opy_(config):
  if bstack1llllll11_opy_ (u"ࠧࡪࡵࡓࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹ࠭ଓ") in config:
    del(config[bstack1llllll11_opy_ (u"ࠨ࡫ࡶࡔࡱࡧࡹࡸࡴ࡬࡫࡭ࡺࠧଔ")])
    return False
  if bstack1l11l111l_opy_() < version.parse(bstack1llllll11_opy_ (u"ࠩ࠶࠲࠹࠴࠰ࠨକ")):
    return False
  if bstack1l11l111l_opy_() >= version.parse(bstack1llllll11_opy_ (u"ࠪ࠸࠳࠷࠮࠶ࠩଖ")):
    return True
  if bstack1llllll11_opy_ (u"ࠫࡺࡹࡥࡘ࠵ࡆࠫଗ") in config and config[bstack1llllll11_opy_ (u"ࠬࡻࡳࡦ࡙࠶ࡇࠬଘ")] == False:
    return False
  else:
    return True
def bstack111l1ll_opy_(config, index = 0):
  global bstack111ll1ll1_opy_
  bstack1l11lll_opy_ = {}
  caps = bstack11ll1l11l_opy_ + bstack1llllll_opy_
  if bstack111ll1ll1_opy_:
    caps += bstack1lllll111_opy_
  for key in config:
    if key in caps + [bstack1llllll11_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩଙ")]:
      continue
    bstack1l11lll_opy_[key] = config[key]
  if bstack1llllll11_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪଚ") in config:
    for bstack1ll11ll11_opy_ in config[bstack1llllll11_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫଛ")][index]:
      if bstack1ll11ll11_opy_ in caps + [bstack1llllll11_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡑࡥࡲ࡫ࠧଜ"), bstack1llllll11_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵ࡚ࡪࡸࡳࡪࡱࡱࠫଝ")]:
        continue
      bstack1l11lll_opy_[bstack1ll11ll11_opy_] = config[bstack1llllll11_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧଞ")][index][bstack1ll11ll11_opy_]
  bstack1l11lll_opy_[bstack1llllll11_opy_ (u"ࠬ࡮࡯ࡴࡶࡑࡥࡲ࡫ࠧଟ")] = socket.gethostname()
  if bstack1llllll11_opy_ (u"࠭ࡶࡦࡴࡶ࡭ࡴࡴࠧଠ") in bstack1l11lll_opy_:
    del(bstack1l11lll_opy_[bstack1llllll11_opy_ (u"ࠧࡷࡧࡵࡷ࡮ࡵ࡮ࠨଡ")])
  return bstack1l11lll_opy_
def bstack1lll11l_opy_(config):
  global bstack111ll1ll1_opy_
  bstack11lll11l_opy_ = {}
  caps = bstack1llllll_opy_
  if bstack111ll1ll1_opy_:
    caps+= bstack1lllll111_opy_
  for key in caps:
    if key in config:
      bstack11lll11l_opy_[key] = config[key]
  return bstack11lll11l_opy_
def bstack1111l11l_opy_(bstack1l11lll_opy_, bstack11lll11l_opy_):
  bstack111l111l1_opy_ = {}
  for key in bstack1l11lll_opy_.keys():
    if key in bstack111l11l1_opy_:
      bstack111l111l1_opy_[bstack111l11l1_opy_[key]] = bstack1l11lll_opy_[key]
    else:
      bstack111l111l1_opy_[key] = bstack1l11lll_opy_[key]
  for key in bstack11lll11l_opy_:
    if key in bstack111l11l1_opy_:
      bstack111l111l1_opy_[bstack111l11l1_opy_[key]] = bstack11lll11l_opy_[key]
    else:
      bstack111l111l1_opy_[key] = bstack11lll11l_opy_[key]
  return bstack111l111l1_opy_
def bstack1111lllll_opy_(config, index = 0):
  global bstack111ll1ll1_opy_
  config = copy.deepcopy(config)
  caps = {}
  bstack11lll11l_opy_ = bstack1lll11l_opy_(config)
  bstack1ll111lll_opy_ = bstack1llllll_opy_
  bstack1ll111lll_opy_ += bstack11l1l11l_opy_
  if bstack111ll1ll1_opy_:
    bstack1ll111lll_opy_ += bstack1lllll111_opy_
  if bstack1llllll11_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫଢ") in config:
    if bstack1llllll11_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡑࡥࡲ࡫ࠧଣ") in config[bstack1llllll11_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ତ")][index]:
      caps[bstack1llllll11_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠩଥ")] = config[bstack1llllll11_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨଦ")][index][bstack1llllll11_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡎࡢ࡯ࡨࠫଧ")]
    if bstack1llllll11_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨନ") in config[bstack1llllll11_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫ଩")][index]:
      caps[bstack1llllll11_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠪପ")] = str(config[bstack1llllll11_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ଫ")][index][bstack1llllll11_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶ࡛࡫ࡲࡴ࡫ࡲࡲࠬବ")])
    bstack11ll1ll_opy_ = {}
    for bstack111111ll_opy_ in bstack1ll111lll_opy_:
      if bstack111111ll_opy_ in config[bstack1llllll11_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨଭ")][index]:
        if bstack111111ll_opy_ == bstack1llllll11_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡗࡧࡵࡷ࡮ࡵ࡮ࠨମ"):
          try:
            bstack11ll1ll_opy_[bstack111111ll_opy_] = str(config[bstack1llllll11_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪଯ")][index][bstack111111ll_opy_] * 1.0)
          except:
            bstack11ll1ll_opy_[bstack111111ll_opy_] = str(config[bstack1llllll11_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫର")][index][bstack111111ll_opy_])
        else:
          bstack11ll1ll_opy_[bstack111111ll_opy_] = config[bstack1llllll11_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬ଱")][index][bstack111111ll_opy_]
        del(config[bstack1llllll11_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ଲ")][index][bstack111111ll_opy_])
    bstack11lll11l_opy_ = update(bstack11lll11l_opy_, bstack11ll1ll_opy_)
  bstack1l11lll_opy_ = bstack111l1ll_opy_(config, index)
  for bstack1l1ll11l_opy_ in bstack1llllll_opy_ + [bstack1llllll11_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠩଳ"), bstack1llllll11_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ࠭଴")]:
    if bstack1l1ll11l_opy_ in bstack1l11lll_opy_:
      bstack11lll11l_opy_[bstack1l1ll11l_opy_] = bstack1l11lll_opy_[bstack1l1ll11l_opy_]
      del(bstack1l11lll_opy_[bstack1l1ll11l_opy_])
  if bstack11ll_opy_(config):
    bstack1l11lll_opy_[bstack1llllll11_opy_ (u"࠭ࡵࡴࡧ࡚࠷ࡈ࠭ଵ")] = True
    caps.update(bstack11lll11l_opy_)
    caps[bstack1llllll11_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࠺ࡰࡲࡷ࡭ࡴࡴࡳࠨଶ")] = bstack1l11lll_opy_
  else:
    bstack1l11lll_opy_[bstack1llllll11_opy_ (u"ࠨࡷࡶࡩ࡜࠹ࡃࠨଷ")] = False
    caps.update(bstack1111l11l_opy_(bstack1l11lll_opy_, bstack11lll11l_opy_))
    if bstack1llllll11_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡑࡥࡲ࡫ࠧସ") in caps:
      caps[bstack1llllll11_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࠫହ")] = caps[bstack1llllll11_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠩ଺")]
      del(caps[bstack1llllll11_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡔࡡ࡮ࡧࠪ଻")])
    if bstack1llllll11_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡖࡦࡴࡶ࡭ࡴࡴ଼ࠧ") in caps:
      caps[bstack1llllll11_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡠࡸࡨࡶࡸ࡯࡯࡯ࠩଽ")] = caps[bstack1llllll11_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡘࡨࡶࡸ࡯࡯࡯ࠩା")]
      del(caps[bstack1llllll11_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠪି")])
  return caps
def bstack11ll1l1l1_opy_():
  global bstack1l1111ll1_opy_
  if bstack1l11l111l_opy_() <= version.parse(bstack1llllll11_opy_ (u"ࠪ࠷࠳࠷࠳࠯࠲ࠪୀ")):
    if bstack1l1111ll1_opy_ != bstack1llllll11_opy_ (u"ࠫࠬୁ"):
      return bstack1llllll11_opy_ (u"ࠧ࡮ࡴࡵࡲ࠽࠳࠴ࠨୂ") + bstack1l1111ll1_opy_ + bstack1llllll11_opy_ (u"ࠨ࠺࠹࠲࠲ࡻࡩ࠵ࡨࡶࡤࠥୃ")
    return bstack1ll111ll_opy_
  if  bstack1l1111ll1_opy_ != bstack1llllll11_opy_ (u"ࠧࠨୄ"):
    return bstack1llllll11_opy_ (u"ࠣࡪࡷࡸࡵࡹ࠺࠰࠱ࠥ୅") + bstack1l1111ll1_opy_ + bstack1llllll11_opy_ (u"ࠤ࠲ࡻࡩ࠵ࡨࡶࡤࠥ୆")
  return bstack1111l111_opy_
def bstack1l1lll1l1_opy_(options):
  return hasattr(options, bstack1llllll11_opy_ (u"ࠪࡷࡪࡺ࡟ࡤࡣࡳࡥࡧ࡯࡬ࡪࡶࡼࠫେ"))
def update(d, u):
  for k, v in u.items():
    if isinstance(v, collections.abc.Mapping):
      d[k] = update(d.get(k, {}), v)
    else:
      if isinstance(v, list):
        d[k] = d.get(k, []) + v
      else:
        d[k] = v
  return d
def bstack11l11_opy_(options, bstack1111lll1_opy_):
  for bstack11l1111ll_opy_ in bstack1111lll1_opy_:
    if bstack11l1111ll_opy_ in [bstack1llllll11_opy_ (u"ࠫࡦࡸࡧࡴࠩୈ"), bstack1llllll11_opy_ (u"ࠬ࡫ࡸࡵࡧࡱࡷ࡮ࡵ࡮ࡴࠩ୉")]:
      next
    if bstack11l1111ll_opy_ in options._experimental_options:
      options._experimental_options[bstack11l1111ll_opy_]= update(options._experimental_options[bstack11l1111ll_opy_], bstack1111lll1_opy_[bstack11l1111ll_opy_])
    else:
      options.add_experimental_option(bstack11l1111ll_opy_, bstack1111lll1_opy_[bstack11l1111ll_opy_])
  if bstack1llllll11_opy_ (u"࠭ࡡࡳࡩࡶࠫ୊") in bstack1111lll1_opy_:
    for arg in bstack1111lll1_opy_[bstack1llllll11_opy_ (u"ࠧࡢࡴࡪࡷࠬୋ")]:
      options.add_argument(arg)
    del(bstack1111lll1_opy_[bstack1llllll11_opy_ (u"ࠨࡣࡵ࡫ࡸ࠭ୌ")])
  if bstack1llllll11_opy_ (u"ࠩࡨࡼࡹ࡫࡮ࡴ࡫ࡲࡲࡸ୍࠭") in bstack1111lll1_opy_:
    for ext in bstack1111lll1_opy_[bstack1llllll11_opy_ (u"ࠪࡩࡽࡺࡥ࡯ࡵ࡬ࡳࡳࡹࠧ୎")]:
      options.add_extension(ext)
    del(bstack1111lll1_opy_[bstack1llllll11_opy_ (u"ࠫࡪࡾࡴࡦࡰࡶ࡭ࡴࡴࡳࠨ୏")])
def bstack1l1l11l_opy_(options, bstack111l1_opy_):
  if bstack1llllll11_opy_ (u"ࠬࡶࡲࡦࡨࡶࠫ୐") in bstack111l1_opy_:
    for bstack1lll1llll_opy_ in bstack111l1_opy_[bstack1llllll11_opy_ (u"࠭ࡰࡳࡧࡩࡷࠬ୑")]:
      if bstack1lll1llll_opy_ in options._preferences:
        options._preferences[bstack1lll1llll_opy_] = update(options._preferences[bstack1lll1llll_opy_], bstack111l1_opy_[bstack1llllll11_opy_ (u"ࠧࡱࡴࡨࡪࡸ࠭୒")][bstack1lll1llll_opy_])
      else:
        options.set_preference(bstack1lll1llll_opy_, bstack111l1_opy_[bstack1llllll11_opy_ (u"ࠨࡲࡵࡩ࡫ࡹࠧ୓")][bstack1lll1llll_opy_])
  if bstack1llllll11_opy_ (u"ࠩࡤࡶ࡬ࡹࠧ୔") in bstack111l1_opy_:
    for arg in bstack111l1_opy_[bstack1llllll11_opy_ (u"ࠪࡥࡷ࡭ࡳࠨ୕")]:
      options.add_argument(arg)
def bstack1l1l1_opy_(options, bstack111l1l_opy_):
  if bstack1llllll11_opy_ (u"ࠫࡼ࡫ࡢࡷ࡫ࡨࡻࠬୖ") in bstack111l1l_opy_:
    options.use_webview(bool(bstack111l1l_opy_[bstack1llllll11_opy_ (u"ࠬࡽࡥࡣࡸ࡬ࡩࡼ࠭ୗ")]))
  bstack11l11_opy_(options, bstack111l1l_opy_)
def bstack11ll11ll_opy_(options, bstack111llll_opy_):
  for bstack1l111lll_opy_ in bstack111llll_opy_:
    if bstack1l111lll_opy_ in [bstack1llllll11_opy_ (u"࠭ࡴࡦࡥ࡫ࡲࡴࡲ࡯ࡨࡻࡓࡶࡪࡼࡩࡦࡹࠪ୘"), bstack1llllll11_opy_ (u"ࠧࡢࡴࡪࡷࠬ୙")]:
      next
    options.set_capability(bstack1l111lll_opy_, bstack111llll_opy_[bstack1l111lll_opy_])
  if bstack1llllll11_opy_ (u"ࠨࡣࡵ࡫ࡸ࠭୚") in bstack111llll_opy_:
    for arg in bstack111llll_opy_[bstack1llllll11_opy_ (u"ࠩࡤࡶ࡬ࡹࠧ୛")]:
      options.add_argument(arg)
  if bstack1llllll11_opy_ (u"ࠪࡸࡪࡩࡨ࡯ࡱ࡯ࡳ࡬ࡿࡐࡳࡧࡹ࡭ࡪࡽࠧଡ଼") in bstack111llll_opy_:
    options.bstack1l11l11_opy_(bool(bstack111llll_opy_[bstack1llllll11_opy_ (u"ࠫࡹ࡫ࡣࡩࡰࡲࡰࡴ࡭ࡹࡑࡴࡨࡺ࡮࡫ࡷࠨଢ଼")]))
def bstack1l1l1ll_opy_(options, bstack11l1ll_opy_):
  for bstack1l1l1111_opy_ in bstack11l1ll_opy_:
    if bstack1l1l1111_opy_ in [bstack1llllll11_opy_ (u"ࠬࡧࡤࡥ࡫ࡷ࡭ࡴࡴࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴࠩ୞"), bstack1llllll11_opy_ (u"࠭ࡡࡳࡩࡶࠫୟ")]:
      next
    options._options[bstack1l1l1111_opy_] = bstack11l1ll_opy_[bstack1l1l1111_opy_]
  if bstack1llllll11_opy_ (u"ࠧࡢࡦࡧ࡭ࡹ࡯࡯࡯ࡣ࡯ࡓࡵࡺࡩࡰࡰࡶࠫୠ") in bstack11l1ll_opy_:
    for bstack111l1ll1l_opy_ in bstack11l1ll_opy_[bstack1llllll11_opy_ (u"ࠨࡣࡧࡨ࡮ࡺࡩࡰࡰࡤࡰࡔࡶࡴࡪࡱࡱࡷࠬୡ")]:
      options.bstack1lll11ll_opy_(
          bstack111l1ll1l_opy_, bstack11l1ll_opy_[bstack1llllll11_opy_ (u"ࠩࡤࡨࡩ࡯ࡴࡪࡱࡱࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭ୢ")][bstack111l1ll1l_opy_])
  if bstack1llllll11_opy_ (u"ࠪࡥࡷ࡭ࡳࠨୣ") in bstack11l1ll_opy_:
    for arg in bstack11l1ll_opy_[bstack1llllll11_opy_ (u"ࠫࡦࡸࡧࡴࠩ୤")]:
      options.add_argument(arg)
def bstack11l111ll_opy_(options, caps):
  if not hasattr(options, bstack1llllll11_opy_ (u"ࠬࡑࡅ࡚ࠩ୥")):
    return
  if options.KEY == bstack1llllll11_opy_ (u"࠭ࡧࡰࡱࡪ࠾ࡨ࡮ࡲࡰ࡯ࡨࡓࡵࡺࡩࡰࡰࡶࠫ୦") and options.KEY in caps:
    bstack11l11_opy_(options, caps[bstack1llllll11_opy_ (u"ࠧࡨࡱࡲ࡫࠿ࡩࡨࡳࡱࡰࡩࡔࡶࡴࡪࡱࡱࡷࠬ୧")])
  elif options.KEY == bstack1llllll11_opy_ (u"ࠨ࡯ࡲࡾ࠿࡬ࡩࡳࡧࡩࡳࡽࡕࡰࡵ࡫ࡲࡲࡸ࠭୨") and options.KEY in caps:
    bstack1l1l11l_opy_(options, caps[bstack1llllll11_opy_ (u"ࠩࡰࡳࡿࡀࡦࡪࡴࡨࡪࡴࡾࡏࡱࡶ࡬ࡳࡳࡹࠧ୩")])
  elif options.KEY == bstack1llllll11_opy_ (u"ࠪࡷࡦ࡬ࡡࡳ࡫࠱ࡳࡵࡺࡩࡰࡰࡶࠫ୪") and options.KEY in caps:
    bstack11ll11ll_opy_(options, caps[bstack1llllll11_opy_ (u"ࠫࡸࡧࡦࡢࡴ࡬࠲ࡴࡶࡴࡪࡱࡱࡷࠬ୫")])
  elif options.KEY == bstack1llllll11_opy_ (u"ࠬࡳࡳ࠻ࡧࡧ࡫ࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭୬") and options.KEY in caps:
    bstack1l1l1_opy_(options, caps[bstack1llllll11_opy_ (u"࠭࡭ࡴ࠼ࡨࡨ࡬࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧ୭")])
  elif options.KEY == bstack1llllll11_opy_ (u"ࠧࡴࡧ࠽࡭ࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭୮") and options.KEY in caps:
    bstack1l1l1ll_opy_(options, caps[bstack1llllll11_opy_ (u"ࠨࡵࡨ࠾࡮࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧ୯")])
def bstack1ll11l_opy_(caps):
  global bstack111ll1ll1_opy_
  if bstack111ll1ll1_opy_:
    if bstack111ll11ll_opy_() < version.parse(bstack1llllll11_opy_ (u"ࠩ࠵࠲࠸࠴࠰ࠨ୰")):
      return None
    else:
      from appium.options.common.base import AppiumOptions
      options = AppiumOptions().load_capabilities(caps)
      return options
  else:
    browser = bstack1llllll11_opy_ (u"ࠪࡧ࡭ࡸ࡯࡮ࡧࠪୱ")
    if bstack1llllll11_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠩ୲") in caps:
      browser = caps[bstack1llllll11_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡔࡡ࡮ࡧࠪ୳")]
    elif bstack1llllll11_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࠧ୴") in caps:
      browser = caps[bstack1llllll11_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࠨ୵")]
    browser = str(browser).lower()
    if browser == bstack1llllll11_opy_ (u"ࠨ࡫ࡳ࡬ࡴࡴࡥࠨ୶") or browser == bstack1llllll11_opy_ (u"ࠩ࡬ࡴࡦࡪࠧ୷"):
      browser = bstack1llllll11_opy_ (u"ࠪࡷࡦ࡬ࡡࡳ࡫ࠪ୸")
    if browser == bstack1llllll11_opy_ (u"ࠫࡸࡧ࡭ࡴࡷࡱ࡫ࠬ୹"):
      browser = bstack1llllll11_opy_ (u"ࠬࡩࡨࡳࡱࡰࡩࠬ୺")
    if browser not in [bstack1llllll11_opy_ (u"࠭ࡣࡩࡴࡲࡱࡪ࠭୻"), bstack1llllll11_opy_ (u"ࠧࡦࡦࡪࡩࠬ୼"), bstack1llllll11_opy_ (u"ࠨ࡫ࡨࠫ୽"), bstack1llllll11_opy_ (u"ࠩࡶࡥ࡫ࡧࡲࡪࠩ୾"), bstack1llllll11_opy_ (u"ࠪࡪ࡮ࡸࡥࡧࡱࡻࠫ୿")]:
      return None
    try:
      package = bstack1llllll11_opy_ (u"ࠫࡸ࡫࡬ࡦࡰ࡬ࡹࡲ࠴ࡷࡦࡤࡧࡶ࡮ࡼࡥࡳ࠰ࡾࢁ࠳ࡵࡰࡵ࡫ࡲࡲࡸ࠭஀").format(browser)
      name = bstack1llllll11_opy_ (u"ࠬࡕࡰࡵ࡫ࡲࡲࡸ࠭஁")
      browser_options = getattr(__import__(package, fromlist=[name]), name)
      options = browser_options()
      if not bstack1l1lll1l1_opy_(options):
        return None
      for bstack1l1ll11l_opy_ in caps.keys():
        options.set_capability(bstack1l1ll11l_opy_, caps[bstack1l1ll11l_opy_])
      bstack11l111ll_opy_(options, caps)
      return options
    except Exception as e:
      logger.debug(str(e))
      return None
def bstack11ll1l1l_opy_(options, bstack11l1l_opy_):
  if not bstack1l1lll1l1_opy_(options):
    return
  for bstack1l1ll11l_opy_ in bstack11l1l_opy_.keys():
    if bstack1l1ll11l_opy_ in bstack11l1l11l_opy_:
      next
    if bstack1l1ll11l_opy_ in options._caps and type(options._caps[bstack1l1ll11l_opy_]) in [dict, list]:
      options._caps[bstack1l1ll11l_opy_] = update(options._caps[bstack1l1ll11l_opy_], bstack11l1l_opy_[bstack1l1ll11l_opy_])
    else:
      options.set_capability(bstack1l1ll11l_opy_, bstack11l1l_opy_[bstack1l1ll11l_opy_])
  bstack11l111ll_opy_(options, bstack11l1l_opy_)
  if bstack1llllll11_opy_ (u"࠭࡭ࡰࡼ࠽ࡨࡪࡨࡵࡨࡩࡨࡶࡆࡪࡤࡳࡧࡶࡷࠬஂ") in options._caps:
    if options._caps[bstack1llllll11_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡏࡣࡰࡩࠬஃ")] and options._caps[bstack1llllll11_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡐࡤࡱࡪ࠭஄")].lower() != bstack1llllll11_opy_ (u"ࠩࡩ࡭ࡷ࡫ࡦࡰࡺࠪஅ"):
      del options._caps[bstack1llllll11_opy_ (u"ࠪࡱࡴࢀ࠺ࡥࡧࡥࡹ࡬࡭ࡥࡳࡃࡧࡨࡷ࡫ࡳࡴࠩஆ")]
def bstack1lll11l1l_opy_(proxy_config):
  if bstack1llllll11_opy_ (u"ࠫ࡭ࡺࡴࡱࡵࡓࡶࡴࡾࡹࠨஇ") in proxy_config:
    proxy_config[bstack1llllll11_opy_ (u"ࠬࡹࡳ࡭ࡒࡵࡳࡽࡿࠧஈ")] = proxy_config[bstack1llllll11_opy_ (u"࠭ࡨࡵࡶࡳࡷࡕࡸ࡯ࡹࡻࠪஉ")]
    del(proxy_config[bstack1llllll11_opy_ (u"ࠧࡩࡶࡷࡴࡸࡖࡲࡰࡺࡼࠫஊ")])
  if bstack1llllll11_opy_ (u"ࠨࡲࡵࡳࡽࡿࡔࡺࡲࡨࠫ஋") in proxy_config and proxy_config[bstack1llllll11_opy_ (u"ࠩࡳࡶࡴࡾࡹࡕࡻࡳࡩࠬ஌")].lower() != bstack1llllll11_opy_ (u"ࠪࡨ࡮ࡸࡥࡤࡶࠪ஍"):
    proxy_config[bstack1llllll11_opy_ (u"ࠫࡵࡸ࡯ࡹࡻࡗࡽࡵ࡫ࠧஎ")] = bstack1llllll11_opy_ (u"ࠬࡳࡡ࡯ࡷࡤࡰࠬஏ")
  if bstack1llllll11_opy_ (u"࠭ࡰࡳࡱࡻࡽࡆࡻࡴࡰࡥࡲࡲ࡫࡯ࡧࡖࡴ࡯ࠫஐ") in proxy_config:
    proxy_config[bstack1llllll11_opy_ (u"ࠧࡱࡴࡲࡼࡾ࡚ࡹࡱࡧࠪ஑")] = bstack1llllll11_opy_ (u"ࠨࡲࡤࡧࠬஒ")
  return proxy_config
def bstack1l1l11ll1_opy_(config, proxy):
  from selenium.webdriver.common.proxy import Proxy
  if not bstack1llllll11_opy_ (u"ࠩࡳࡶࡴࡾࡹࠨஓ") in config:
    return proxy
  config[bstack1llllll11_opy_ (u"ࠪࡴࡷࡵࡸࡺࠩஔ")] = bstack1lll11l1l_opy_(config[bstack1llllll11_opy_ (u"ࠫࡵࡸ࡯ࡹࡻࠪக")])
  if proxy == None:
    proxy = Proxy(config[bstack1llllll11_opy_ (u"ࠬࡶࡲࡰࡺࡼࠫ஖")])
  return proxy
def bstack1llllllll_opy_(self):
  global CONFIG
  global bstack11l1ll1_opy_
  try:
    proxy = bstack111l1l1l_opy_(CONFIG)
    if proxy:
      if proxy.endswith(bstack1llllll11_opy_ (u"࠭࠮ࡱࡣࡦࠫ஗")):
        proxies = bstack1lll1l11_opy_(proxy, bstack11ll1l1l1_opy_())
        if len(proxies) > 0:
          protocol, bstack11111l1_opy_ = proxies.popitem()
          if bstack1llllll11_opy_ (u"ࠢ࠻࠱࠲ࠦ஘") in bstack11111l1_opy_:
            return bstack11111l1_opy_
          else:
            return bstack1llllll11_opy_ (u"ࠣࡪࡷࡸࡵࡀ࠯࠰ࠤங") + bstack11111l1_opy_
      else:
        return proxy
  except Exception as e:
    logger.error(bstack1llllll11_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡸ࡫ࡴࡵ࡫ࡱ࡫ࠥࡶࡲࡰࡺࡼࠤࡺࡸ࡬ࠡ࠼ࠣࡿࢂࠨச").format(str(e)))
  return bstack11l1ll1_opy_(self)
def bstack1l11ll1l_opy_():
  global CONFIG
  return bstack1llllll11_opy_ (u"ࠪ࡬ࡹࡺࡰࡑࡴࡲࡼࡾ࠭஛") in CONFIG or bstack1llllll11_opy_ (u"ࠫ࡭ࡺࡴࡱࡵࡓࡶࡴࡾࡹࠨஜ") in CONFIG
def bstack111l1l1l_opy_(config):
  if not bstack1l11ll1l_opy_():
    return
  if config.get(bstack1llllll11_opy_ (u"ࠬ࡮ࡴࡵࡲࡓࡶࡴࡾࡹࠨ஝")):
    return config.get(bstack1llllll11_opy_ (u"࠭ࡨࡵࡶࡳࡔࡷࡵࡸࡺࠩஞ"))
  if config.get(bstack1llllll11_opy_ (u"ࠧࡩࡶࡷࡴࡸࡖࡲࡰࡺࡼࠫட")):
    return config.get(bstack1llllll11_opy_ (u"ࠨࡪࡷࡸࡵࡹࡐࡳࡱࡻࡽࠬ஠"))
def bstack11l11l1ll_opy_(url):
  try:
      result = urlparse(url)
      return all([result.scheme, result.netloc])
  except:
      return False
def bstack111l1ll11_opy_(bstack1l1ll11l1_opy_, bstack111l1llll_opy_):
  from pypac import get_pac
  from pypac import PACSession
  from pypac.parser import PACFile
  import socket
  if os.path.isfile(bstack1l1ll11l1_opy_):
    with open(bstack1l1ll11l1_opy_) as f:
      pac = PACFile(f.read())
  elif bstack11l11l1ll_opy_(bstack1l1ll11l1_opy_):
    pac = get_pac(url=bstack1l1ll11l1_opy_)
  else:
    raise Exception(bstack1llllll11_opy_ (u"ࠩࡓࡥࡨࠦࡦࡪ࡮ࡨࠤࡩࡵࡥࡴࠢࡱࡳࡹࠦࡥࡹ࡫ࡶࡸ࠿ࠦࡻࡾࠩ஡").format(bstack1l1ll11l1_opy_))
  session = PACSession(pac)
  try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((bstack1llllll11_opy_ (u"ࠥ࠼࠳࠾࠮࠹࠰࠻ࠦ஢"), 80))
    bstack1111ll1_opy_ = s.getsockname()[0]
    s.close()
  except:
    bstack1111ll1_opy_ = bstack1llllll11_opy_ (u"ࠫ࠵࠴࠰࠯࠲࠱࠴ࠬண")
  proxy_url = session.get_pac().find_proxy_for_url(bstack111l1llll_opy_, bstack1111ll1_opy_)
  return proxy_url
def bstack1lll1l11_opy_(bstack1l1ll11l1_opy_, bstack111l1llll_opy_):
  proxies = {}
  global bstack1lll1l11l_opy_
  if bstack1llllll11_opy_ (u"ࠬࡖࡁࡄࡡࡓࡖࡔ࡞࡙ࠨத") in globals():
    return bstack1lll1l11l_opy_
  try:
    proxy = bstack111l1ll11_opy_(bstack1l1ll11l1_opy_,bstack111l1llll_opy_)
    if bstack1llllll11_opy_ (u"ࠨࡄࡊࡔࡈࡇ࡙ࠨ஥") in proxy:
      proxies = {}
    elif bstack1llllll11_opy_ (u"ࠢࡉࡖࡗࡔࠧ஦") in proxy or bstack1llllll11_opy_ (u"ࠣࡊࡗࡘࡕ࡙ࠢ஧") in proxy or bstack1llllll11_opy_ (u"ࠤࡖࡓࡈࡑࡓࠣந") in proxy:
      bstack1l111ll1_opy_ = proxy.split(bstack1llllll11_opy_ (u"ࠥࠤࠧன"))
      if bstack1llllll11_opy_ (u"ࠦ࠿࠵࠯ࠣப") in bstack1llllll11_opy_ (u"ࠧࠨ஫").join(bstack1l111ll1_opy_[1:]):
        proxies = {
          bstack1llllll11_opy_ (u"࠭ࡨࡵࡶࡳࡷࠬ஬"): bstack1llllll11_opy_ (u"ࠢࠣ஭").join(bstack1l111ll1_opy_[1:])
        }
      else:
        proxies = {
          bstack1llllll11_opy_ (u"ࠨࡪࡷࡸࡵࡹࠧம") : str(bstack1l111ll1_opy_[0]).lower()+ bstack1llllll11_opy_ (u"ࠤ࠽࠳࠴ࠨய") + bstack1llllll11_opy_ (u"ࠥࠦர").join(bstack1l111ll1_opy_[1:])
        }
    elif bstack1llllll11_opy_ (u"ࠦࡕࡘࡏ࡙࡛ࠥற") in proxy:
      bstack1l111ll1_opy_ = proxy.split(bstack1llllll11_opy_ (u"ࠧࠦࠢல"))
      if bstack1llllll11_opy_ (u"ࠨ࠺࠰࠱ࠥள") in bstack1llllll11_opy_ (u"ࠢࠣழ").join(bstack1l111ll1_opy_[1:]):
        proxies = {
          bstack1llllll11_opy_ (u"ࠨࡪࡷࡸࡵࡹࠧவ"): bstack1llllll11_opy_ (u"ࠤࠥஶ").join(bstack1l111ll1_opy_[1:])
        }
      else:
        proxies = {
          bstack1llllll11_opy_ (u"ࠪ࡬ࡹࡺࡰࡴࠩஷ"): bstack1llllll11_opy_ (u"ࠦ࡭ࡺࡴࡱ࠼࠲࠳ࠧஸ") + bstack1llllll11_opy_ (u"ࠧࠨஹ").join(bstack1l111ll1_opy_[1:])
        }
    else:
      proxies = {
        bstack1llllll11_opy_ (u"࠭ࡨࡵࡶࡳࡷࠬ஺"): proxy
      }
  except Exception as e:
    logger.error(bstack111l1l11_opy_.format(bstack1l1ll11l1_opy_, str(e)))
  bstack1lll1l11l_opy_ = proxies
  return proxies
def bstack1lll1l1l1_opy_(config, bstack111l1llll_opy_):
  proxy = bstack111l1l1l_opy_(config)
  proxies = {}
  if config.get(bstack1llllll11_opy_ (u"ࠧࡩࡶࡷࡴࡕࡸ࡯ࡹࡻࠪ஻")) or config.get(bstack1llllll11_opy_ (u"ࠨࡪࡷࡸࡵࡹࡐࡳࡱࡻࡽࠬ஼")):
    if proxy.endswith(bstack1llllll11_opy_ (u"ࠩ࠱ࡴࡦࡩࠧ஽")):
      proxies = bstack1lll1l11_opy_(proxy,bstack111l1llll_opy_)
    else:
      proxies = {
        bstack1llllll11_opy_ (u"ࠪ࡬ࡹࡺࡰࡴࠩா"): proxy
      }
  return proxies
def bstack11ll1111l_opy_():
  return bstack1l11ll1l_opy_() and bstack1l11l111l_opy_() >= version.parse(bstack1l1l1l1l_opy_)
def bstack1l11l1l11_opy_(config):
  bstack111ll1l_opy_ = {}
  if bstack1llllll11_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡘࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࡐࡲࡷ࡭ࡴࡴࡳࠨி") in config:
    bstack111ll1l_opy_ =  config[bstack1llllll11_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴࠩீ")]
  if bstack1llllll11_opy_ (u"࠭࡬ࡰࡥࡤࡰࡔࡶࡴࡪࡱࡱࡷࠬு") in config:
    bstack111ll1l_opy_ = config[bstack1llllll11_opy_ (u"ࠧ࡭ࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭ூ")]
  proxy = bstack111l1l1l_opy_(config)
  if proxy:
    if proxy.endswith(bstack1llllll11_opy_ (u"ࠨ࠰ࡳࡥࡨ࠭௃")) and os.path.isfile(proxy):
      bstack111ll1l_opy_[bstack1llllll11_opy_ (u"ࠩ࠰ࡴࡦࡩ࠭ࡧ࡫࡯ࡩࠬ௄")] = proxy
    else:
      parsed_url = None
      if proxy.endswith(bstack1llllll11_opy_ (u"ࠪ࠲ࡵࡧࡣࠨ௅")):
        proxies = bstack1lll1l1l1_opy_(config, bstack11ll1l1l1_opy_())
        if len(proxies) > 0:
          protocol, bstack11111l1_opy_ = proxies.popitem()
          if bstack1llllll11_opy_ (u"ࠦ࠿࠵࠯ࠣெ") in bstack11111l1_opy_:
            parsed_url = urlparse(bstack11111l1_opy_)
          else:
            parsed_url = urlparse(protocol + bstack1llllll11_opy_ (u"ࠧࡀ࠯࠰ࠤே") + bstack11111l1_opy_)
      else:
        parsed_url = urlparse(proxy)
      if parsed_url and parsed_url.hostname: bstack111ll1l_opy_[bstack1llllll11_opy_ (u"࠭ࡰࡳࡱࡻࡽࡍࡵࡳࡵࠩை")] = str(parsed_url.hostname)
      if parsed_url and parsed_url.port: bstack111ll1l_opy_[bstack1llllll11_opy_ (u"ࠧࡱࡴࡲࡼࡾࡖ࡯ࡳࡶࠪ௉")] = str(parsed_url.port)
      if parsed_url and parsed_url.username: bstack111ll1l_opy_[bstack1llllll11_opy_ (u"ࠨࡲࡵࡳࡽࡿࡕࡴࡧࡵࠫொ")] = str(parsed_url.username)
      if parsed_url and parsed_url.password: bstack111ll1l_opy_[bstack1llllll11_opy_ (u"ࠩࡳࡶࡴࡾࡹࡑࡣࡶࡷࠬோ")] = str(parsed_url.password)
  return bstack111ll1l_opy_
def bstack11l1l1l1_opy_(config):
  if bstack1llllll11_opy_ (u"ࠪࡸࡪࡹࡴࡄࡱࡱࡸࡪࡾࡴࡐࡲࡷ࡭ࡴࡴࡳࠨௌ") in config:
    return config[bstack1llllll11_opy_ (u"ࠫࡹ࡫ࡳࡵࡅࡲࡲࡹ࡫ࡸࡵࡑࡳࡸ࡮ࡵ࡮ࡴ்ࠩ")]
  return {}
def bstack11l11l1_opy_(caps):
  global bstack11111l11_opy_
  if bstack1llllll11_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯࠿ࡵࡰࡵ࡫ࡲࡲࡸ࠭௎") in caps:
    caps[bstack1llllll11_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡀ࡯ࡱࡶ࡬ࡳࡳࡹࠧ௏")][bstack1llllll11_opy_ (u"ࠧ࡭ࡱࡦࡥࡱ࠭ௐ")] = True
    if bstack11111l11_opy_:
      caps[bstack1llllll11_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫࠻ࡱࡳࡸ࡮ࡵ࡮ࡴࠩ௑")][bstack1llllll11_opy_ (u"ࠩ࡯ࡳࡨࡧ࡬ࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫ௒")] = bstack11111l11_opy_
  else:
    caps[bstack1llllll11_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰࡯ࡳࡨࡧ࡬ࠨ௓")] = True
    if bstack11111l11_opy_:
      caps[bstack1llllll11_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡰࡴࡩࡡ࡭ࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬ௔")] = bstack11111l11_opy_
def bstack1ll1l1ll_opy_():
  global CONFIG
  if bstack1llllll11_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࠩ௕") in CONFIG and CONFIG[bstack1llllll11_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࠪ௖")]:
    bstack111ll1l_opy_ = bstack1l11l1l11_opy_(CONFIG)
    bstack1lll111l_opy_(CONFIG[bstack1llllll11_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡋࡦࡻࠪௗ")], bstack111ll1l_opy_)
def bstack1lll111l_opy_(key, bstack111ll1l_opy_):
  global bstack11111111_opy_
  logger.info(bstack1llll1_opy_)
  try:
    bstack11111111_opy_ = Local()
    bstack1l111ll_opy_ = {bstack1llllll11_opy_ (u"ࠨ࡭ࡨࡽࠬ௘"): key}
    bstack1l111ll_opy_.update(bstack111ll1l_opy_)
    logger.debug(bstack11l11lll_opy_.format(str(bstack1l111ll_opy_)))
    bstack11111111_opy_.start(**bstack1l111ll_opy_)
    if bstack11111111_opy_.isRunning():
      logger.info(bstack1lllll11l_opy_)
  except Exception as e:
    bstack1l1lll1_opy_(bstack1ll1l1l1l_opy_.format(str(e)))
def bstack11l1l1l11_opy_():
  global bstack11111111_opy_
  if bstack11111111_opy_.isRunning():
    logger.info(bstack11l1l1ll_opy_)
    bstack11111111_opy_.stop()
  bstack11111111_opy_ = None
def bstack1l1l11l11_opy_(bstack1l1l1lll_opy_=[]):
  global CONFIG
  bstack1l11llll1_opy_ = []
  bstack1111ll1ll_opy_ = [bstack1llllll11_opy_ (u"ࠩࡲࡷࠬ௙"), bstack1llllll11_opy_ (u"ࠪࡳࡸ࡜ࡥࡳࡵ࡬ࡳࡳ࠭௚"), bstack1llllll11_opy_ (u"ࠫࡩ࡫ࡶࡪࡥࡨࡒࡦࡳࡥࠨ௛"), bstack1llllll11_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡖࡦࡴࡶ࡭ࡴࡴࠧ௜"), bstack1llllll11_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡎࡢ࡯ࡨࠫ௝"), bstack1llllll11_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨ௞")]
  try:
    for err in bstack1l1l1lll_opy_:
      bstack1l1l1l111_opy_ = {}
      for k in bstack1111ll1ll_opy_:
        val = CONFIG[bstack1llllll11_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫ௟")][int(err[bstack1llllll11_opy_ (u"ࠩ࡬ࡲࡩ࡫ࡸࠨ௠")])].get(k)
        if val:
          bstack1l1l1l111_opy_[k] = val
      bstack1l1l1l111_opy_[bstack1llllll11_opy_ (u"ࠪࡸࡪࡹࡴࡴࠩ௡")] = {
        err[bstack1llllll11_opy_ (u"ࠫࡳࡧ࡭ࡦࠩ௢")]: err[bstack1llllll11_opy_ (u"ࠬ࡫ࡲࡳࡱࡵࠫ௣")]
      }
      bstack1l11llll1_opy_.append(bstack1l1l1l111_opy_)
  except Exception as e:
    logger.debug(bstack1llllll11_opy_ (u"࠭ࡅࡳࡴࡲࡶࠥ࡯࡮ࠡࡨࡲࡶࡲࡧࡴࡵ࡫ࡱ࡫ࠥࡪࡡࡵࡣࠣࡪࡴࡸࠠࡦࡸࡨࡲࡹࡀࠠࠨ௤") +str(e))
  finally:
    return bstack1l11llll1_opy_
def bstack1lll111_opy_():
  global bstack11ll11l_opy_
  global bstack1lll1ll1l_opy_
  global bstack11l11l11l_opy_
  if bstack11ll11l_opy_:
    logger.warning(bstack11lll111_opy_.format(str(bstack11ll11l_opy_)))
  logger.info(bstack1lll1l1l_opy_)
  global bstack11111111_opy_
  if bstack11111111_opy_:
    bstack11l1l1l11_opy_()
  try:
    for driver in bstack1lll1ll1l_opy_:
      driver.quit()
  except Exception as e:
    pass
  logger.info(bstack1l11lll11_opy_)
  bstack1lllll11_opy_()
  if len(bstack11l11l11l_opy_) > 0:
    message = bstack1l1l11l11_opy_(bstack11l11l11l_opy_)
    bstack1lllll11_opy_(message)
  else:
    bstack1lllll11_opy_()
def bstack1l11lll1l_opy_(self, *args):
  logger.error(bstack1llll1111_opy_)
  bstack1lll111_opy_()
  sys.exit(1)
def bstack1l1lll1_opy_(err):
  logger.critical(bstack11lllll1l_opy_.format(str(err)))
  bstack1lllll11_opy_(bstack11lllll1l_opy_.format(str(err)))
  atexit.unregister(bstack1lll111_opy_)
  sys.exit(1)
def bstack1ll1_opy_(error, message):
  logger.critical(str(error))
  logger.critical(message)
  bstack1lllll11_opy_(message)
  atexit.unregister(bstack1lll111_opy_)
  sys.exit(1)
def bstack11lllllll_opy_():
  global CONFIG
  global bstack11l1_opy_
  global bstack1l111l11l_opy_
  global bstack1llll1ll1_opy_
  CONFIG = bstack1111l11_opy_()
  bstack1ll1ll11l_opy_()
  bstack11ll1111_opy_()
  CONFIG = bstack11lll111l_opy_(CONFIG)
  update(CONFIG, bstack1l111l11l_opy_)
  update(CONFIG, bstack11l1_opy_)
  CONFIG = bstack1l1lll11l_opy_(CONFIG)
  if bstack1llllll11_opy_ (u"ࠧࡢࡷࡷࡳࡲࡧࡴࡪࡱࡱࠫ௥") in CONFIG and str(CONFIG[bstack1llllll11_opy_ (u"ࠨࡣࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠬ௦")]).lower() == bstack1llllll11_opy_ (u"ࠩࡩࡥࡱࡹࡥࠨ௧"):
    bstack1llll1ll1_opy_ = False
  if (bstack1llllll11_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡐࡤࡱࡪ࠭௨") in CONFIG and bstack1llllll11_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠧ௩") in bstack11l1_opy_) or (bstack1llllll11_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡒࡦࡳࡥࠨ௪") in CONFIG and bstack1llllll11_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦࠩ௫") not in bstack1l111l11l_opy_):
    if os.getenv(bstack1llllll11_opy_ (u"ࠧࡃࡕࡗࡅࡈࡑ࡟ࡄࡑࡐࡆࡎࡔࡅࡅࡡࡅ࡙ࡎࡒࡄࡠࡋࡇࠫ௬")):
      CONFIG[bstack1llllll11_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪ௭")] = os.getenv(bstack1llllll11_opy_ (u"ࠩࡅࡗ࡙ࡇࡃࡌࡡࡆࡓࡒࡈࡉࡏࡇࡇࡣࡇ࡛ࡉࡍࡆࡢࡍࡉ࠭௮"))
    else:
      bstack111ll1lll_opy_()
  elif (bstack1llllll11_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡐࡤࡱࡪ࠭௯") not in CONFIG and bstack1llllll11_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭௰") in CONFIG) or (bstack1llllll11_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡒࡦࡳࡥࠨ௱") in bstack1l111l11l_opy_ and bstack1llllll11_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦࠩ௲") not in bstack11l1_opy_):
    del(CONFIG[bstack1llllll11_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩ௳")])
  if bstack111ll1l1_opy_(CONFIG):
    bstack1l1lll1_opy_(bstack1ll1ll1_opy_)
  bstack1lllll1l1_opy_()
  bstack1ll1llll_opy_()
  if bstack111ll1ll1_opy_:
    CONFIG[bstack1llllll11_opy_ (u"ࠨࡣࡳࡴࠬ௴")] = bstack1l1l11l1_opy_(CONFIG)
    logger.info(bstack1ll11111_opy_.format(CONFIG[bstack1llllll11_opy_ (u"ࠩࡤࡴࡵ࠭௵")]))
def bstack1ll1llll_opy_():
  global CONFIG
  global bstack111ll1ll1_opy_
  if bstack1llllll11_opy_ (u"ࠪࡥࡵࡶࠧ௶") in CONFIG:
    try:
      from appium import version
    except Exception as e:
      bstack1ll1_opy_(e, bstack1l11l111_opy_)
    bstack111ll1ll1_opy_ = True
def bstack1l1l11l1_opy_(config):
  bstack1ll1ll1l1_opy_ = bstack1llllll11_opy_ (u"ࠫࠬ௷")
  app = config[bstack1llllll11_opy_ (u"ࠬࡧࡰࡱࠩ௸")]
  if isinstance(app, str):
    if os.path.splitext(app)[1] in bstack1ll1ll1l_opy_:
      if os.path.exists(app):
        bstack1ll1ll1l1_opy_ = bstack1l111ll11_opy_(config, app)
      elif bstack1l1ll1111_opy_(app):
        bstack1ll1ll1l1_opy_ = app
      else:
        bstack1l1lll1_opy_(bstack1l1lllll1_opy_.format(app))
    else:
      if bstack1l1ll1111_opy_(app):
        bstack1ll1ll1l1_opy_ = app
      elif os.path.exists(app):
        bstack1ll1ll1l1_opy_ = bstack1l111ll11_opy_(app)
      else:
        bstack1l1lll1_opy_(bstack1ll11l1l_opy_)
  else:
    if len(app) > 2:
      bstack1l1lll1_opy_(bstack1l11lllll_opy_)
    elif len(app) == 2:
      if bstack1llllll11_opy_ (u"࠭ࡰࡢࡶ࡫ࠫ௹") in app and bstack1llllll11_opy_ (u"ࠧࡤࡷࡶࡸࡴࡳ࡟ࡪࡦࠪ௺") in app:
        if os.path.exists(app[bstack1llllll11_opy_ (u"ࠨࡲࡤࡸ࡭࠭௻")]):
          bstack1ll1ll1l1_opy_ = bstack1l111ll11_opy_(config, app[bstack1llllll11_opy_ (u"ࠩࡳࡥࡹ࡮ࠧ௼")], app[bstack1llllll11_opy_ (u"ࠪࡧࡺࡹࡴࡰ࡯ࡢ࡭ࡩ࠭௽")])
        else:
          bstack1l1lll1_opy_(bstack1l1lllll1_opy_.format(app))
      else:
        bstack1l1lll1_opy_(bstack1l11lllll_opy_)
    else:
      for key in app:
        if key in bstack1l1111ll_opy_:
          if key == bstack1llllll11_opy_ (u"ࠫࡵࡧࡴࡩࠩ௾"):
            if os.path.exists(app[key]):
              bstack1ll1ll1l1_opy_ = bstack1l111ll11_opy_(config, app[key])
            else:
              bstack1l1lll1_opy_(bstack1l1lllll1_opy_.format(app))
          else:
            bstack1ll1ll1l1_opy_ = app[key]
        else:
          bstack1l1lll1_opy_(bstack11llllll_opy_)
  return bstack1ll1ll1l1_opy_
def bstack1l1ll1111_opy_(bstack1ll1ll1l1_opy_):
  import re
  bstack1llll1ll_opy_ = re.compile(bstack1llllll11_opy_ (u"ࡷࠨ࡞࡜ࡣ࠰ࡾࡆ࠳࡚࠱࠯࠼ࡠࡤ࠴࡜࠮࡟࠭ࠨࠧ௿"))
  bstack1l11l1ll_opy_ = re.compile(bstack1llllll11_opy_ (u"ࡸࠢ࡟࡝ࡤ࠱ࡿࡇ࡛࠭࠲࠰࠽ࡡࡥ࠮࡝࠯ࡠ࠮࠴ࡡࡡ࠮ࡼࡄ࠱࡟࠶࠭࠺࡞ࡢ࠲ࡡ࠳࡝ࠫࠦࠥఀ"))
  if bstack1llllll11_opy_ (u"ࠧࡣࡵ࠽࠳࠴࠭ఁ") in bstack1ll1ll1l1_opy_ or re.fullmatch(bstack1llll1ll_opy_, bstack1ll1ll1l1_opy_) or re.fullmatch(bstack1l11l1ll_opy_, bstack1ll1ll1l1_opy_):
    return True
  else:
    return False
def bstack1l111ll11_opy_(config, path, bstack111l11lll_opy_=None):
  import requests
  from requests_toolbelt.multipart.encoder import MultipartEncoder
  import hashlib
  md5_hash = hashlib.md5(open(os.path.abspath(path), bstack1llllll11_opy_ (u"ࠨࡴࡥࠫం")).read()).hexdigest()
  bstack1ll111_opy_ = bstack1ll1l1l_opy_(md5_hash)
  bstack1ll1ll1l1_opy_ = None
  if bstack1ll111_opy_:
    logger.info(bstack1_opy_.format(bstack1ll111_opy_, md5_hash))
    return bstack1ll111_opy_
  bstack1l11ll111_opy_ = MultipartEncoder(
    fields={
        bstack1llllll11_opy_ (u"ࠩࡩ࡭ࡱ࡫ࠧః"): (os.path.basename(path), open(os.path.abspath(path), bstack1llllll11_opy_ (u"ࠪࡶࡧ࠭ఄ")), bstack1llllll11_opy_ (u"ࠫࡹ࡫ࡸࡵ࠱ࡳࡰࡦ࡯࡮ࠨఅ")),
        bstack1llllll11_opy_ (u"ࠬࡩࡵࡴࡶࡲࡱࡤ࡯ࡤࠨఆ"): bstack111l11lll_opy_
    }
  )
  response = requests.post(bstack1l111111_opy_, data=bstack1l11ll111_opy_,
                         headers={bstack1llllll11_opy_ (u"࠭ࡃࡰࡰࡷࡩࡳࡺ࠭ࡕࡻࡳࡩࠬఇ"): bstack1l11ll111_opy_.content_type}, auth=(config[bstack1llllll11_opy_ (u"ࠧࡶࡵࡨࡶࡓࡧ࡭ࡦࠩఈ")], config[bstack1llllll11_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡌࡧࡼࠫఉ")]))
  try:
    res = json.loads(response.text)
    bstack1ll1ll1l1_opy_ = res[bstack1llllll11_opy_ (u"ࠩࡤࡴࡵࡥࡵࡳ࡮ࠪఊ")]
    logger.info(bstack1ll111111_opy_.format(bstack1ll1ll1l1_opy_))
    bstack1llll11l1_opy_(md5_hash, bstack1ll1ll1l1_opy_)
  except ValueError as err:
    bstack1l1lll1_opy_(bstack1l_opy_.format(str(err)))
  return bstack1ll1ll1l1_opy_
def bstack1lllll1l1_opy_():
  global CONFIG
  global bstack1ll11l111_opy_
  bstack11111lll_opy_ = 0
  bstack1ll11ll1l_opy_ = 1
  if bstack1llllll11_opy_ (u"ࠪࡴࡦࡸࡡ࡭࡮ࡨࡰࡸࡖࡥࡳࡒ࡯ࡥࡹ࡬࡯ࡳ࡯ࠪఋ") in CONFIG:
    bstack1ll11ll1l_opy_ = CONFIG[bstack1llllll11_opy_ (u"ࠫࡵࡧࡲࡢ࡮࡯ࡩࡱࡹࡐࡦࡴࡓࡰࡦࡺࡦࡰࡴࡰࠫఌ")]
  if bstack1llllll11_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨ఍") in CONFIG:
    bstack11111lll_opy_ = len(CONFIG[bstack1llllll11_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩఎ")])
  bstack1ll11l111_opy_ = int(bstack1ll11ll1l_opy_) * int(bstack11111lll_opy_)
def bstack1ll1l1l_opy_(md5_hash):
  bstack1lll1l1_opy_ = os.path.join(os.path.expanduser(bstack1llllll11_opy_ (u"ࠧࡿࠩఏ")), bstack1llllll11_opy_ (u"ࠨ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠨఐ"), bstack1llllll11_opy_ (u"ࠩࡤࡴࡵ࡛ࡰ࡭ࡱࡤࡨࡒࡊ࠵ࡉࡣࡶ࡬࠳ࡰࡳࡰࡰࠪ఑"))
  if os.path.exists(bstack1lll1l1_opy_):
    bstack1l1llll1l_opy_ = json.load(open(bstack1lll1l1_opy_,bstack1llllll11_opy_ (u"ࠪࡶࡧ࠭ఒ")))
    if md5_hash in bstack1l1llll1l_opy_:
      bstack11lllll_opy_ = bstack1l1llll1l_opy_[md5_hash]
      bstack1ll11ll1_opy_ = datetime.datetime.now()
      bstack1lll1l111_opy_ = datetime.datetime.strptime(bstack11lllll_opy_[bstack1llllll11_opy_ (u"ࠫࡹ࡯࡭ࡦࡵࡷࡥࡲࡶࠧఓ")], bstack1llllll11_opy_ (u"ࠬࠫࡤ࠰ࠧࡰ࠳ࠪ࡟ࠠࠦࡊ࠽ࠩࡒࡀࠥࡔࠩఔ"))
      if (bstack1ll11ll1_opy_ - bstack1lll1l111_opy_).days > 60:
        return None
      elif version.parse(str(__version__)) > version.parse(bstack11lllll_opy_[bstack1llllll11_opy_ (u"࠭ࡳࡥ࡭ࡢࡺࡪࡸࡳࡪࡱࡱࠫక")]):
        return None
      return bstack11lllll_opy_[bstack1llllll11_opy_ (u"ࠧࡪࡦࠪఖ")]
  else:
    return None
def bstack1llll11l1_opy_(md5_hash, bstack1ll1ll1l1_opy_):
  bstack1ll1lllll_opy_ = os.path.join(os.path.expanduser(bstack1llllll11_opy_ (u"ࠨࢀࠪగ")), bstack1llllll11_opy_ (u"ࠩ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠩఘ"))
  if not os.path.exists(bstack1ll1lllll_opy_):
    os.makedirs(bstack1ll1lllll_opy_)
  bstack1lll1l1_opy_ = os.path.join(os.path.expanduser(bstack1llllll11_opy_ (u"ࠪࢂࠬఙ")), bstack1llllll11_opy_ (u"ࠫ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠫచ"), bstack1llllll11_opy_ (u"ࠬࡧࡰࡱࡗࡳࡰࡴࡧࡤࡎࡆ࠸ࡌࡦࡹࡨ࠯࡬ࡶࡳࡳ࠭ఛ"))
  bstack1l1l1l1_opy_ = {
    bstack1llllll11_opy_ (u"࠭ࡩࡥࠩజ"): bstack1ll1ll1l1_opy_,
    bstack1llllll11_opy_ (u"ࠧࡵ࡫ࡰࡩࡸࡺࡡ࡮ࡲࠪఝ"): datetime.datetime.strftime(datetime.datetime.now(), bstack1llllll11_opy_ (u"ࠨࠧࡧ࠳ࠪࡳ࠯࡛ࠦࠣࠩࡍࡀࠥࡎ࠼ࠨࡗࠬఞ")),
    bstack1llllll11_opy_ (u"ࠩࡶࡨࡰࡥࡶࡦࡴࡶ࡭ࡴࡴࠧట"): str(__version__)
  }
  if os.path.exists(bstack1lll1l1_opy_):
    bstack1l1llll1l_opy_ = json.load(open(bstack1lll1l1_opy_,bstack1llllll11_opy_ (u"ࠪࡶࡧ࠭ఠ")))
  else:
    bstack1l1llll1l_opy_ = {}
  bstack1l1llll1l_opy_[md5_hash] = bstack1l1l1l1_opy_
  with open(bstack1lll1l1_opy_, bstack1llllll11_opy_ (u"ࠦࡼ࠱ࠢడ")) as outfile:
    json.dump(bstack1l1llll1l_opy_, outfile)
def bstack1l1ll11_opy_(self):
  return
def bstack111l11ll_opy_(self):
  return
def bstack1llll111_opy_(self):
  from selenium.webdriver.remote.webdriver import WebDriver
  WebDriver.quit(self)
def bstack1lll1_opy_(self):
  global bstack1l1l1l_opy_
  global bstack1ll11l11_opy_
  global bstack1ll11ll_opy_
  try:
    if bstack1llllll11_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࠬఢ") in bstack1l1l1l_opy_ and self.session_id != None:
      bstack1l1l111l1_opy_ = bstack1llllll11_opy_ (u"࠭ࡰࡢࡵࡶࡩࡩ࠭ణ") if len(threading.current_thread().bstackTestErrorMessages) == 0 else bstack1llllll11_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪࠧత")
      bstack1lllll1l_opy_ = bstack111l1l1ll_opy_(bstack1llllll11_opy_ (u"ࠨࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡘࡺࡡࡵࡷࡶࠫథ"), bstack1llllll11_opy_ (u"ࠩࠪద"), bstack1l1l111l1_opy_, bstack1llllll11_opy_ (u"ࠪ࠰ࠥ࠭ధ").join(threading.current_thread().bstackTestErrorMessages), bstack1llllll11_opy_ (u"ࠫࠬన"), bstack1llllll11_opy_ (u"ࠬ࠭఩"))
      if self != None:
        self.execute_script(bstack1lllll1l_opy_)
  except Exception as e:
    logger.debug(bstack1llllll11_opy_ (u"ࠨࡅࡳࡴࡲࡶࠥࡽࡨࡪ࡮ࡨࠤࡲࡧࡲ࡬࡫ࡱ࡫ࠥࡹࡴࡢࡶࡸࡷ࠿ࠦࠢప") + str(e))
  bstack1ll11ll_opy_(self)
  self.session_id = None
def bstack1111lll11_opy_(self, command_executor,
        desired_capabilities=None, browser_profile=None, proxy=None,
        keep_alive=True, file_detector=None, options=None):
  global CONFIG
  global bstack1ll11l11_opy_
  global bstack1111lll1l_opy_
  global bstack1l1ll1ll_opy_
  global bstack11l11lll1_opy_
  global bstack1l11l1111_opy_
  global bstack1l1l1l_opy_
  global bstack1llll1l_opy_
  global bstack1lll1ll1l_opy_
  global bstack11l1l11_opy_
  CONFIG[bstack1llllll11_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࡙ࡄࡌࠩఫ")] = str(bstack1l1l1l_opy_) + str(__version__)
  command_executor = bstack11ll1l1l1_opy_()
  logger.debug(bstack1lll1ll_opy_.format(command_executor))
  proxy = bstack1l1l11ll1_opy_(CONFIG, proxy)
  bstack111lll1_opy_ = 0 if bstack1111lll1l_opy_ < 0 else bstack1111lll1l_opy_
  try:
    if bstack11l11lll1_opy_ is True:
      bstack111lll1_opy_ = int(multiprocessing.current_process().name)
    elif bstack1l11l1111_opy_ is True:
      bstack111lll1_opy_ = int(threading.current_thread().name)
  except:
    bstack111lll1_opy_ = 0
  bstack11l1l_opy_ = bstack1111lllll_opy_(CONFIG, bstack111lll1_opy_)
  logger.debug(bstack11l111lll_opy_.format(str(bstack11l1l_opy_)))
  if bstack1llllll11_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡌࡰࡥࡤࡰࠬబ") in CONFIG and CONFIG[bstack1llllll11_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡍࡱࡦࡥࡱ࠭భ")]:
    bstack11l11l1_opy_(bstack11l1l_opy_)
  if desired_capabilities:
    bstack1ll111l11_opy_ = bstack11lll111l_opy_(desired_capabilities)
    bstack1ll111l11_opy_[bstack1llllll11_opy_ (u"ࠪࡹࡸ࡫ࡗ࠴ࡅࠪమ")] = bstack11ll_opy_(CONFIG)
    bstack11l1lll11_opy_ = bstack1111lllll_opy_(bstack1ll111l11_opy_)
    if bstack11l1lll11_opy_:
      bstack11l1l_opy_ = update(bstack11l1lll11_opy_, bstack11l1l_opy_)
    desired_capabilities = None
  if options:
    bstack11ll1l1l_opy_(options, bstack11l1l_opy_)
  if not options:
    options = bstack1ll11l_opy_(bstack11l1l_opy_)
  if proxy and bstack1l11l111l_opy_() >= version.parse(bstack1llllll11_opy_ (u"ࠫ࠹࠴࠱࠱࠰࠳ࠫయ")):
    options.proxy(proxy)
  if options and bstack1l11l111l_opy_() >= version.parse(bstack1llllll11_opy_ (u"ࠬ࠹࠮࠹࠰࠳ࠫర")):
    desired_capabilities = None
  if (
      not options and not desired_capabilities
  ) or (
      bstack1l11l111l_opy_() < version.parse(bstack1llllll11_opy_ (u"࠭࠳࠯࠺࠱࠴ࠬఱ")) and not desired_capabilities
  ):
    desired_capabilities = {}
    desired_capabilities.update(bstack11l1l_opy_)
  logger.info(bstack111lll_opy_)
  if bstack1l11l111l_opy_() >= version.parse(bstack1llllll11_opy_ (u"ࠧ࠵࠰࠴࠴࠳࠶ࠧల")):
    bstack1llll1l_opy_(self, command_executor=command_executor,
          options=options, keep_alive=keep_alive, file_detector=file_detector)
  elif bstack1l11l111l_opy_() >= version.parse(bstack1llllll11_opy_ (u"ࠨ࠵࠱࠼࠳࠶ࠧళ")):
    bstack1llll1l_opy_(self, command_executor=command_executor,
          desired_capabilities=desired_capabilities, options=options,
          browser_profile=browser_profile, proxy=proxy,
          keep_alive=keep_alive, file_detector=file_detector)
  elif bstack1l11l111l_opy_() >= version.parse(bstack1llllll11_opy_ (u"ࠩ࠵࠲࠺࠹࠮࠱ࠩఴ")):
    bstack1llll1l_opy_(self, command_executor=command_executor,
          desired_capabilities=desired_capabilities,
          browser_profile=browser_profile, proxy=proxy,
          keep_alive=keep_alive, file_detector=file_detector)
  else:
    bstack1llll1l_opy_(self, command_executor=command_executor,
          desired_capabilities=desired_capabilities,
          browser_profile=browser_profile, proxy=proxy,
          keep_alive=keep_alive)
  try:
    bstack1111llll_opy_ = bstack1llllll11_opy_ (u"ࠪࠫవ")
    if bstack1l11l111l_opy_() >= version.parse(bstack1llllll11_opy_ (u"ࠫ࠹࠴࠰࠯࠲ࡥ࠵ࠬశ")):
      bstack1111llll_opy_ = self.caps.get(bstack1llllll11_opy_ (u"ࠧࡵࡰࡵ࡫ࡰࡥࡱࡎࡵࡣࡗࡵࡰࠧష"))
    else:
      bstack1111llll_opy_ = self.capabilities.get(bstack1llllll11_opy_ (u"ࠨ࡯ࡱࡶ࡬ࡱࡦࡲࡈࡶࡤࡘࡶࡱࠨస"))
    if bstack1111llll_opy_:
      if bstack1l11l111l_opy_() <= version.parse(bstack1llllll11_opy_ (u"ࠧ࠴࠰࠴࠷࠳࠶ࠧహ")):
        self.command_executor._url = bstack1llllll11_opy_ (u"ࠣࡪࡷࡸࡵࡀ࠯࠰ࠤ఺") + bstack1l1111ll1_opy_ + bstack1llllll11_opy_ (u"ࠤ࠽࠼࠵࠵ࡷࡥ࠱࡫ࡹࡧࠨ఻")
      else:
        self.command_executor._url = bstack1llllll11_opy_ (u"ࠥ࡬ࡹࡺࡰࡴ࠼࠲࠳఼ࠧ") + bstack1111llll_opy_ + bstack1llllll11_opy_ (u"ࠦ࠴ࡽࡤ࠰ࡪࡸࡦࠧఽ")
      logger.debug(bstack111lll1l_opy_.format(bstack1111llll_opy_))
    else:
      logger.debug(bstack1l1ll1l1l_opy_.format(bstack1llllll11_opy_ (u"ࠧࡕࡰࡵ࡫ࡰࡥࡱࠦࡈࡶࡤࠣࡲࡴࡺࠠࡧࡱࡸࡲࡩࠨా")))
  except Exception as e:
    logger.debug(bstack1l1ll1l1l_opy_.format(e))
  if bstack1llllll11_opy_ (u"࠭ࡲࡰࡤࡲࡸࠬి") in bstack1l1l1l_opy_:
    bstack11l1ll111_opy_(bstack1111lll1l_opy_, bstack11l1l11_opy_)
  bstack1ll11l11_opy_ = self.session_id
  if bstack1llllll11_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺࠧీ") in bstack1l1l1l_opy_:
    threading.current_thread().bstack1l1l11_opy_ = self.session_id
    threading.current_thread().bstackSessionDriver = self
    threading.current_thread().bstackTestErrorMessages = []
  bstack1lll1ll1l_opy_.append(self)
  if bstack1llllll11_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫు") in CONFIG and bstack1llllll11_opy_ (u"ࠩࡶࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧూ") in CONFIG[bstack1llllll11_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ృ")][bstack111lll1_opy_]:
    bstack1l1ll1ll_opy_ = CONFIG[bstack1llllll11_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧౄ")][bstack111lll1_opy_][bstack1llllll11_opy_ (u"ࠬࡹࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠪ౅")]
  logger.debug(bstack1l11l_opy_.format(bstack1ll11l11_opy_))
try:
  try:
    import Browser
    from subprocess import Popen
    def bstack1ll11111l_opy_(self, args, bufsize=-1, executable=None,
              stdin=None, stdout=None, stderr=None,
              preexec_fn=None, close_fds=True,
              shell=False, cwd=None, env=None, universal_newlines=None,
              startupinfo=None, creationflags=0,
              restore_signals=True, start_new_session=False,
              pass_fds=(), *, user=None, group=None, extra_groups=None,
              encoding=None, errors=None, text=None, umask=-1, pipesize=-1):
      global CONFIG
      global bstack1l111111l_opy_
      if(bstack1llllll11_opy_ (u"ࠨࡩ࡯ࡦࡨࡼ࠳ࡰࡳࠣె") in args[1]):
        with open(os.path.join(os.path.expanduser(bstack1llllll11_opy_ (u"ࠧࡿࠩే")), bstack1llllll11_opy_ (u"ࠨ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠨై"), bstack1llllll11_opy_ (u"ࠩ࠱ࡷࡪࡹࡳࡪࡱࡱ࡭ࡩࡹ࠮ࡵࡺࡷࠫ౉")), bstack1llllll11_opy_ (u"ࠪࡻࠬొ")) as fp:
          fp.write(bstack1llllll11_opy_ (u"ࠦࠧో"))
        if(not os.path.exists(os.path.join(os.path.dirname(args[1]), bstack1llllll11_opy_ (u"ࠧ࡯࡮ࡥࡧࡻࡣࡧࡹࡴࡢࡥ࡮࠲࡯ࡹࠢౌ")))):
          with open(args[1], bstack1llllll11_opy_ (u"࠭ࡲࠨ్")) as f:
            lines = f.readlines()
            index = next((i for i, line in enumerate(lines) if bstack1llllll11_opy_ (u"ࠧࡢࡵࡼࡲࡨࠦࡦࡶࡰࡦࡸ࡮ࡵ࡮ࠡࡡࡱࡩࡼࡖࡡࡨࡧࠫࡧࡴࡴࡴࡦࡺࡷ࠰ࠥࡶࡡࡨࡧࠣࡁࠥࡼ࡯ࡪࡦࠣ࠴࠮࠭౎") in line), None)
            if index is not None:
                lines.insert(index+2, bstack1111llll1_opy_)
            lines.insert(1, bstack1ll1llll1_opy_)
            f.seek(0)
            with open(os.path.join(os.path.dirname(args[1]), bstack1llllll11_opy_ (u"ࠣ࡫ࡱࡨࡪࡾ࡟ࡣࡵࡷࡥࡨࡱ࠮࡫ࡵࠥ౏")), bstack1llllll11_opy_ (u"ࠩࡺࠫ౐")) as bstack111ll1l11_opy_:
              bstack111ll1l11_opy_.writelines(lines)
        CONFIG[bstack1llllll11_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡕࡇࡏࠬ౑")] = str(bstack1l1l1l_opy_) + str(__version__)
        bstack111lll1_opy_ = 0 if bstack1111lll1l_opy_ < 0 else bstack1111lll1l_opy_
        if bstack11l11lll1_opy_ is True:
          bstack111lll1_opy_ = int(threading.current_thread().getName())
        CONFIG[bstack1llllll11_opy_ (u"ࠦࡺࡹࡥࡘ࠵ࡆࠦ౒")] = False
        CONFIG[bstack1llllll11_opy_ (u"ࠧ࡯ࡳࡑ࡮ࡤࡽࡼࡸࡩࡨࡪࡷࠦ౓")] = True
        bstack11l1l_opy_ = bstack1111lllll_opy_(CONFIG, bstack111lll1_opy_)
        logger.debug(bstack11l111lll_opy_.format(str(bstack11l1l_opy_)))
        if CONFIG[bstack1llllll11_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࠪ౔")]:
          bstack11l11l1_opy_(bstack11l1l_opy_)
        if bstack1llllll11_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵౕࠪ") in CONFIG and bstack1llllll11_opy_ (u"ࠨࡵࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪౖ࠭") in CONFIG[bstack1llllll11_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬ౗")][bstack111lll1_opy_]:
          bstack1l1ll1ll_opy_ = CONFIG[bstack1llllll11_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ౘ")][bstack111lll1_opy_][bstack1llllll11_opy_ (u"ࠫࡸ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠩౙ")]
        args.append(os.path.join(os.path.expanduser(bstack1llllll11_opy_ (u"ࠬࢄࠧౚ")), bstack1llllll11_opy_ (u"࠭࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠭౛"), bstack1llllll11_opy_ (u"ࠧ࠯ࡵࡨࡷࡸ࡯࡯࡯࡫ࡧࡷ࠳ࡺࡸࡵࠩ౜")))
        args.append(str(threading.get_ident()))
        args.append(json.dumps(bstack11l1l_opy_))
        args[1] = os.path.join(os.path.dirname(args[1]), bstack1llllll11_opy_ (u"ࠣ࡫ࡱࡨࡪࡾ࡟ࡣࡵࡷࡥࡨࡱ࠮࡫ࡵࠥౝ"))
      bstack1l111111l_opy_ = True
      return bstack11ll1l1_opy_(self, args, bufsize=bufsize, executable=executable,
                    stdin=stdin, stdout=stdout, stderr=stderr,
                    preexec_fn=preexec_fn, close_fds=close_fds,
                    shell=shell, cwd=cwd, env=env, universal_newlines=universal_newlines,
                    startupinfo=startupinfo, creationflags=creationflags,
                    restore_signals=restore_signals, start_new_session=start_new_session,
                    pass_fds=pass_fds, user=user, group=group, extra_groups=extra_groups,
                    encoding=encoding, errors=errors, text=text, umask=umask, pipesize=pipesize)
  except Exception as e:
    pass
  import playwright._impl._api_structures
  import playwright._impl._helper
  def bstack1ll1ll1ll_opy_(self,
        executablePath = None,
        channel = None,
        args = None,
        ignoreDefaultArgs = None,
        handleSIGINT = None,
        handleSIGTERM = None,
        handleSIGHUP = None,
        timeout = None,
        env = None,
        headless = None,
        devtools = None,
        proxy = None,
        downloadsPath = None,
        slowMo = None,
        tracesDir = None,
        chromiumSandbox = None,
        firefoxUserPrefs = None
        ):
    global CONFIG
    global bstack1ll11l11_opy_
    global bstack1111lll1l_opy_
    global bstack1l1ll1ll_opy_
    global bstack11l11lll1_opy_
    global bstack1l1l1l_opy_
    global bstack1llll1l_opy_
    CONFIG[bstack1llllll11_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡔࡆࡎࠫ౞")] = str(bstack1l1l1l_opy_) + str(__version__)
    bstack111lll1_opy_ = 0 if bstack1111lll1l_opy_ < 0 else bstack1111lll1l_opy_
    if bstack11l11lll1_opy_ is True:
      bstack111lll1_opy_ = int(threading.current_thread().getName())
    CONFIG[bstack1llllll11_opy_ (u"ࠥ࡭ࡸࡖ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠤ౟")] = True
    bstack11l1l_opy_ = bstack1111lllll_opy_(CONFIG, bstack111lll1_opy_)
    logger.debug(bstack11l111lll_opy_.format(str(bstack11l1l_opy_)))
    if CONFIG[bstack1llllll11_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࠨౠ")]:
      bstack11l11l1_opy_(bstack11l1l_opy_)
    if bstack1llllll11_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨౡ") in CONFIG and bstack1llllll11_opy_ (u"࠭ࡳࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠫౢ") in CONFIG[bstack1llllll11_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪౣ")][bstack111lll1_opy_]:
      bstack1l1ll1ll_opy_ = CONFIG[bstack1llllll11_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫ౤")][bstack111lll1_opy_][bstack1llllll11_opy_ (u"ࠩࡶࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧ౥")]
    import urllib
    import json
    bstack1l11l11l_opy_ = bstack1llllll11_opy_ (u"ࠪࡻࡸࡹ࠺࠰࠱ࡦࡨࡵ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮࠱ࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹࡅࡣࡢࡲࡶࡁࠬ౦") + urllib.parse.quote(json.dumps(bstack11l1l_opy_))
    browser = self.connect(bstack1l11l11l_opy_)
    return browser
except Exception as e:
    pass
def bstack1llll111l_opy_():
    global bstack1l111111l_opy_
    try:
        from playwright._impl._browser_type import BrowserType
        BrowserType.launch = bstack1ll1ll1ll_opy_
        bstack1l111111l_opy_ = True
    except Exception as e:
        pass
    try:
      import Browser
      from subprocess import Popen
      Popen.__init__ = bstack1ll11111l_opy_
      bstack1l111111l_opy_ = True
    except Exception as e:
      pass
def bstack1ll1ll11_opy_(context, bstack1l11ll1ll_opy_):
  try:
    context.page.evaluate(bstack1llllll11_opy_ (u"ࠦࡤࠦ࠽࠿ࠢࡾࢁࠧ౧"), bstack1llllll11_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࠤࡤࡧࡹ࡯࡯࡯ࠤ࠽ࠤࠧࡹࡥࡵࡕࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪࠨࠬࠡࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧࡀࠠࡼࠤࡱࡥࡲ࡫ࠢ࠻ࠩ౨")+ json.dumps(bstack1l11ll1ll_opy_) + bstack1llllll11_opy_ (u"ࠨࡽࡾࠤ౩"))
  except Exception as e:
    logger.debug(bstack1llllll11_opy_ (u"ࠢࡦࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࠣࡷࡪࡹࡳࡪࡱࡱࠤࡳࡧ࡭ࡦࠢࡾࢁࠧ౪"), e)
def bstack11l11111_opy_(context, message, level):
  try:
    context.page.evaluate(bstack1llllll11_opy_ (u"ࠣࡡࠣࡁࡃࠦࡻࡾࠤ౫"), bstack1llllll11_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࢀࠨࡡࡤࡶ࡬ࡳࡳࠨ࠺ࠡࠤࡤࡲࡳࡵࡴࡢࡶࡨࠦ࠱ࠦࠢࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠥ࠾ࠥࢁࠢࡥࡣࡷࡥࠧࡀࠧ౬") + json.dumps(message) + bstack1llllll11_opy_ (u"ࠪ࠰ࠧࡲࡥࡷࡧ࡯ࠦ࠿࠭౭") + json.dumps(level) + bstack1llllll11_opy_ (u"ࠫࢂࢃࠧ౮"))
  except Exception as e:
    logger.debug(bstack1llllll11_opy_ (u"ࠧ࡫ࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࠡࡣࡱࡲࡴࡺࡡࡵ࡫ࡲࡲࠥࢁࡽࠣ౯"), e)
def bstack1llll1lll_opy_(context, status, message = bstack1llllll11_opy_ (u"ࠨࠢ౰")):
  try:
    if(status == bstack1llllll11_opy_ (u"ࠢࡧࡣ࡬ࡰࡪࡪࠢ౱")):
      context.page.evaluate(bstack1llllll11_opy_ (u"ࠣࡡࠣࡁࡃࠦࡻࡾࠤ౲"), bstack1llllll11_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࢀࠨࡡࡤࡶ࡬ࡳࡳࠨ࠺ࠡࠤࡶࡩࡹ࡙ࡥࡴࡵ࡬ࡳࡳ࡙ࡴࡢࡶࡸࡷࠧ࠲ࠠࠣࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠦ࠿ࠦࡻࠣࡴࡨࡥࡸࡵ࡮ࠣ࠼ࠪ౳") + json.dumps(bstack1llllll11_opy_ (u"ࠥࡗࡨ࡫࡮ࡢࡴ࡬ࡳࠥ࡬ࡡࡪ࡮ࡨࡨࠥࡽࡩࡵࡪ࠽ࠤࠧ౴") + str(message)) + bstack1llllll11_opy_ (u"ࠫ࠱ࠨࡳࡵࡣࡷࡹࡸࠨ࠺ࠨ౵") + json.dumps(status) + bstack1llllll11_opy_ (u"ࠧࢃࡽࠣ౶"))
    else:
      context.page.evaluate(bstack1llllll11_opy_ (u"ࠨ࡟ࠡ࠿ࡁࠤࢀࢃࠢ౷"), bstack1llllll11_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࠦࡦࡩࡴࡪࡱࡱࠦ࠿ࠦࠢࡴࡧࡷࡗࡪࡹࡳࡪࡱࡱࡗࡹࡧࡴࡶࡵࠥ࠰ࠥࠨࡡࡳࡩࡸࡱࡪࡴࡴࡴࠤ࠽ࠤࢀࠨࡳࡵࡣࡷࡹࡸࠨ࠺ࠨ౸") + json.dumps(status) + bstack1llllll11_opy_ (u"ࠣࡿࢀࠦ౹"))
  except Exception as e:
    logger.debug(bstack1llllll11_opy_ (u"ࠤࡨࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡲ࡯ࡥࡾࡽࡲࡪࡩ࡫ࡸࠥࡹࡥࡵࠢࡶࡩࡸࡹࡩࡰࡰࠣࡷࡹࡧࡴࡶࡵࠣࡿࢂࠨ౺"), e)
def bstack111l1l1l1_opy_(self, url):
  global bstack1llll1l1_opy_
  try:
    bstack11l1l1lll_opy_(url)
  except Exception as err:
    logger.debug(bstack11lll_opy_.format(str(err)))
  try:
    bstack1llll1l1_opy_(self, url)
  except Exception as e:
    try:
      bstack11111ll_opy_ = str(e)
      if any(err_msg in bstack11111ll_opy_ for err_msg in bstack1lll_opy_):
        bstack11l1l1lll_opy_(url, True)
    except Exception as err:
      logger.debug(bstack11lll_opy_.format(str(err)))
    raise e
def bstack1111l1l1_opy_(self):
  global bstack111_opy_
  bstack111_opy_ = self
  return
def bstack11l1lll1l_opy_(self):
  global bstack11l111l_opy_
  bstack11l111l_opy_ = self
  return
def bstack11111l_opy_(self, test):
  global CONFIG
  global bstack11l111l_opy_
  global bstack111_opy_
  global bstack1ll11l11_opy_
  global bstack111l111l_opy_
  global bstack1l1ll1ll_opy_
  global bstack11111_opy_
  global bstack1l111l111_opy_
  global bstack11l111l11_opy_
  global bstack1lll1ll1l_opy_
  try:
    if not bstack1ll11l11_opy_:
      with open(os.path.join(os.path.expanduser(bstack1llllll11_opy_ (u"ࠪࢂࠬ౻")), bstack1llllll11_opy_ (u"ࠫ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠫ౼"), bstack1llllll11_opy_ (u"ࠬ࠴ࡳࡦࡵࡶ࡭ࡴࡴࡩࡥࡵ࠱ࡸࡽࡺࠧ౽"))) as f:
        bstack111l1l11l_opy_ = json.loads(bstack1llllll11_opy_ (u"ࠨࡻࠣ౾") + f.read().strip() + bstack1llllll11_opy_ (u"ࠧࠣࡺࠥ࠾ࠥࠨࡹࠣࠩ౿") + bstack1llllll11_opy_ (u"ࠣࡿࠥಀ"))
        bstack1ll11l11_opy_ = bstack111l1l11l_opy_[str(threading.get_ident())]
  except:
    pass
  if bstack1lll1ll1l_opy_:
    for driver in bstack1lll1ll1l_opy_:
      if bstack1ll11l11_opy_ == driver.session_id:
        if test:
          bstack1l1_opy_ = str(test.data)
        if not bstack1llll1l11_opy_ and bstack1l1_opy_:
          bstack11l1l11l1_opy_ = {
            bstack1llllll11_opy_ (u"ࠩࡤࡧࡹ࡯࡯࡯ࠩಁ"): bstack1llllll11_opy_ (u"ࠪࡷࡪࡺࡓࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠫಂ"),
            bstack1llllll11_opy_ (u"ࠫࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠧಃ"): {
              bstack1llllll11_opy_ (u"ࠬࡴࡡ࡮ࡧࠪ಄"): bstack1l1_opy_
            }
          }
          bstack11l11ll1_opy_ = bstack1llllll11_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽࢀࠫಅ").format(json.dumps(bstack11l1l11l1_opy_))
          driver.execute_script(bstack11l11ll1_opy_)
        if bstack111l111l_opy_:
          bstack11ll11lll_opy_ = {
            bstack1llllll11_opy_ (u"ࠧࡢࡥࡷ࡭ࡴࡴࠧಆ"): bstack1llllll11_opy_ (u"ࠨࡣࡱࡲࡴࡺࡡࡵࡧࠪಇ"),
            bstack1llllll11_opy_ (u"ࠩࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠬಈ"): {
              bstack1llllll11_opy_ (u"ࠪࡨࡦࡺࡡࠨಉ"): bstack1l1_opy_ + bstack1llllll11_opy_ (u"ࠫࠥࡶࡡࡴࡵࡨࡨࠦ࠭ಊ"),
              bstack1llllll11_opy_ (u"ࠬࡲࡥࡷࡧ࡯ࠫಋ"): bstack1llllll11_opy_ (u"࠭ࡩ࡯ࡨࡲࠫಌ")
            }
          }
          bstack11l1l11l1_opy_ = {
            bstack1llllll11_opy_ (u"ࠧࡢࡥࡷ࡭ࡴࡴࠧ಍"): bstack1llllll11_opy_ (u"ࠨࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡘࡺࡡࡵࡷࡶࠫಎ"),
            bstack1llllll11_opy_ (u"ࠩࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠬಏ"): {
              bstack1llllll11_opy_ (u"ࠪࡷࡹࡧࡴࡶࡵࠪಐ"): bstack1llllll11_opy_ (u"ࠫࡵࡧࡳࡴࡧࡧࠫ಑")
            }
          }
          if bstack111l111l_opy_.status == bstack1llllll11_opy_ (u"ࠬࡖࡁࡔࡕࠪಒ"):
            bstack1l1l1llll_opy_ = bstack1llllll11_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽࢀࠫಓ").format(json.dumps(bstack11ll11lll_opy_))
            driver.execute_script(bstack1l1l1llll_opy_)
            bstack11l11ll1_opy_ = bstack1llllll11_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࢁࠬಔ").format(json.dumps(bstack11l1l11l1_opy_))
            driver.execute_script(bstack11l11ll1_opy_)
          elif bstack111l111l_opy_.status == bstack1llllll11_opy_ (u"ࠨࡈࡄࡍࡑ࠭ಕ"):
            reason = bstack1llllll11_opy_ (u"ࠤࠥಖ")
            bstack1ll11llll_opy_ = bstack1l1_opy_ + bstack1llllll11_opy_ (u"ࠪࠤ࡫ࡧࡩ࡭ࡧࡧࠫಗ")
            if bstack111l111l_opy_.message:
              reason = str(bstack111l111l_opy_.message)
              bstack1ll11llll_opy_ = bstack1ll11llll_opy_ + bstack1llllll11_opy_ (u"ࠫࠥࡽࡩࡵࡪࠣࡩࡷࡸ࡯ࡳ࠼ࠣࠫಘ") + reason
            bstack11ll11lll_opy_[bstack1llllll11_opy_ (u"ࠬࡧࡲࡨࡷࡰࡩࡳࡺࡳࠨಙ")] = {
              bstack1llllll11_opy_ (u"࠭࡬ࡦࡸࡨࡰࠬಚ"): bstack1llllll11_opy_ (u"ࠧࡦࡴࡵࡳࡷ࠭ಛ"),
              bstack1llllll11_opy_ (u"ࠨࡦࡤࡸࡦ࠭ಜ"): bstack1ll11llll_opy_
            }
            bstack11l1l11l1_opy_[bstack1llllll11_opy_ (u"ࠩࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠬಝ")] = {
              bstack1llllll11_opy_ (u"ࠪࡷࡹࡧࡴࡶࡵࠪಞ"): bstack1llllll11_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡧࡧࠫಟ"),
              bstack1llllll11_opy_ (u"ࠬࡸࡥࡢࡵࡲࡲࠬಠ"): reason
            }
            bstack1l1l1llll_opy_ = bstack1llllll11_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽࢀࠫಡ").format(json.dumps(bstack11ll11lll_opy_))
            driver.execute_script(bstack1l1l1llll_opy_)
            bstack11l11ll1_opy_ = bstack1llllll11_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࢁࠬಢ").format(json.dumps(bstack11l1l11l1_opy_))
            driver.execute_script(bstack11l11ll1_opy_)
  elif bstack1ll11l11_opy_:
    try:
      data = {}
      bstack1l1_opy_ = None
      if test:
        bstack1l1_opy_ = str(test.data)
      if not bstack1llll1l11_opy_ and bstack1l1_opy_:
        data[bstack1llllll11_opy_ (u"ࠨࡰࡤࡱࡪ࠭ಣ")] = bstack1l1_opy_
      if bstack111l111l_opy_:
        if bstack111l111l_opy_.status == bstack1llllll11_opy_ (u"ࠩࡓࡅࡘ࡙ࠧತ"):
          data[bstack1llllll11_opy_ (u"ࠪࡷࡹࡧࡴࡶࡵࠪಥ")] = bstack1llllll11_opy_ (u"ࠫࡵࡧࡳࡴࡧࡧࠫದ")
        elif bstack111l111l_opy_.status == bstack1llllll11_opy_ (u"ࠬࡌࡁࡊࡎࠪಧ"):
          data[bstack1llllll11_opy_ (u"࠭ࡳࡵࡣࡷࡹࡸ࠭ನ")] = bstack1llllll11_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪࠧ಩")
          if bstack111l111l_opy_.message:
            data[bstack1llllll11_opy_ (u"ࠨࡴࡨࡥࡸࡵ࡮ࠨಪ")] = str(bstack111l111l_opy_.message)
      user = CONFIG[bstack1llllll11_opy_ (u"ࠩࡸࡷࡪࡸࡎࡢ࡯ࡨࠫಫ")]
      key = CONFIG[bstack1llllll11_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵࡎࡩࡾ࠭ಬ")]
      url = bstack1llllll11_opy_ (u"ࠫ࡭ࡺࡴࡱࡵ࠽࠳࠴ࢁࡽ࠻ࡽࢀࡄࡦࡶࡩ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡱࡰ࠳ࡦࡻࡴࡰ࡯ࡤࡸࡪ࠵ࡳࡦࡵࡶ࡭ࡴࡴࡳ࠰ࡽࢀ࠲࡯ࡹ࡯࡯ࠩಭ").format(user, key, bstack1ll11l11_opy_)
      headers = {
        bstack1llllll11_opy_ (u"ࠬࡉ࡯࡯ࡶࡨࡲࡹ࠳ࡴࡺࡲࡨࠫಮ"): bstack1llllll11_opy_ (u"࠭ࡡࡱࡲ࡯࡭ࡨࡧࡴࡪࡱࡱ࠳࡯ࡹ࡯࡯ࠩಯ"),
      }
      if bool(data):
        requests.put(url, json=data, headers=headers)
    except Exception as e:
      logger.error(bstack11ll111l_opy_.format(str(e)))
  if bstack11l111l_opy_:
    bstack1l111l111_opy_(bstack11l111l_opy_)
  if bstack111_opy_:
    bstack11l111l11_opy_(bstack111_opy_)
  bstack11111_opy_(self, test)
def bstack11l11ll11_opy_(self, parent, test, skip_on_failure=None, rpa=False):
  global bstack11l1ll1l1_opy_
  bstack11l1ll1l1_opy_(self, parent, test, skip_on_failure=skip_on_failure, rpa=rpa)
  global bstack111l111l_opy_
  bstack111l111l_opy_ = self._test
def bstack1l11111ll_opy_():
  global bstack1l1lll_opy_
  try:
    if os.path.exists(bstack1l1lll_opy_):
      os.remove(bstack1l1lll_opy_)
  except Exception as e:
    logger.debug(bstack1llllll11_opy_ (u"ࠧࡆࡴࡵࡳࡷࠦࡩ࡯ࠢࡧࡩࡱ࡫ࡴࡪࡰࡪࠤࡷࡵࡢࡰࡶࠣࡶࡪࡶ࡯ࡳࡶࠣࡪ࡮ࡲࡥ࠻ࠢࠪರ") + str(e))
def bstack1111111l_opy_():
  global bstack1l1lll_opy_
  bstack11ll1lll1_opy_ = {}
  try:
    if not os.path.isfile(bstack1l1lll_opy_):
      with open(bstack1l1lll_opy_, bstack1llllll11_opy_ (u"ࠨࡹࠪಱ")):
        pass
      with open(bstack1l1lll_opy_, bstack1llllll11_opy_ (u"ࠤࡺ࠯ࠧಲ")) as outfile:
        json.dump({}, outfile)
    if os.path.exists(bstack1l1lll_opy_):
      bstack11ll1lll1_opy_ = json.load(open(bstack1l1lll_opy_, bstack1llllll11_opy_ (u"ࠪࡶࡧ࠭ಳ")))
  except Exception as e:
    logger.debug(bstack1llllll11_opy_ (u"ࠫࡊࡸࡲࡰࡴࠣ࡭ࡳࠦࡲࡦࡣࡧ࡭ࡳ࡭ࠠࡳࡱࡥࡳࡹࠦࡲࡦࡲࡲࡶࡹࠦࡦࡪ࡮ࡨ࠾ࠥ࠭಴") + str(e))
  finally:
    return bstack11ll1lll1_opy_
def bstack11l1ll111_opy_(platform_index, item_index):
  global bstack1l1lll_opy_
  try:
    bstack11ll1lll1_opy_ = bstack1111111l_opy_()
    bstack11ll1lll1_opy_[item_index] = platform_index
    with open(bstack1l1lll_opy_, bstack1llllll11_opy_ (u"ࠧࡽࠫࠣವ")) as outfile:
      json.dump(bstack11ll1lll1_opy_, outfile)
  except Exception as e:
    logger.debug(bstack1llllll11_opy_ (u"࠭ࡅࡳࡴࡲࡶࠥ࡯࡮ࠡࡹࡵ࡭ࡹ࡯࡮ࡨࠢࡷࡳࠥࡸ࡯ࡣࡱࡷࠤࡷ࡫ࡰࡰࡴࡷࠤ࡫࡯࡬ࡦ࠼ࠣࠫಶ") + str(e))
def bstack11111ll1_opy_(bstack1l1l11111_opy_):
  global CONFIG
  bstack11lllll1_opy_ = bstack1llllll11_opy_ (u"ࠧࠨಷ")
  if not bstack1llllll11_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫಸ") in CONFIG:
    logger.info(bstack1llllll11_opy_ (u"ࠩࡑࡳࠥࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠡࡲࡤࡷࡸ࡫ࡤࠡࡷࡱࡥࡧࡲࡥࠡࡶࡲࠤ࡬࡫࡮ࡦࡴࡤࡸࡪࠦࡲࡦࡲࡲࡶࡹࠦࡦࡰࡴࠣࡖࡴࡨ࡯ࡵࠢࡵࡹࡳ࠭ಹ"))
  try:
    platform = CONFIG[bstack1llllll11_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭಺")][bstack1l1l11111_opy_]
    if bstack1llllll11_opy_ (u"ࠫࡴࡹࠧ಻") in platform:
      bstack11lllll1_opy_ += str(platform[bstack1llllll11_opy_ (u"ࠬࡵࡳࠨ಼")]) + bstack1llllll11_opy_ (u"࠭ࠬࠡࠩಽ")
    if bstack1llllll11_opy_ (u"ࠧࡰࡵ࡙ࡩࡷࡹࡩࡰࡰࠪಾ") in platform:
      bstack11lllll1_opy_ += str(platform[bstack1llllll11_opy_ (u"ࠨࡱࡶ࡚ࡪࡸࡳࡪࡱࡱࠫಿ")]) + bstack1llllll11_opy_ (u"ࠩ࠯ࠤࠬೀ")
    if bstack1llllll11_opy_ (u"ࠪࡨࡪࡼࡩࡤࡧࡑࡥࡲ࡫ࠧು") in platform:
      bstack11lllll1_opy_ += str(platform[bstack1llllll11_opy_ (u"ࠫࡩ࡫ࡶࡪࡥࡨࡒࡦࡳࡥࠨೂ")]) + bstack1llllll11_opy_ (u"ࠬ࠲ࠠࠨೃ")
    if bstack1llllll11_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡗࡧࡵࡷ࡮ࡵ࡮ࠨೄ") in platform:
      bstack11lllll1_opy_ += str(platform[bstack1llllll11_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡘࡨࡶࡸ࡯࡯࡯ࠩ೅")]) + bstack1llllll11_opy_ (u"ࠨ࠮ࠣࠫೆ")
    if bstack1llllll11_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡑࡥࡲ࡫ࠧೇ") in platform:
      bstack11lllll1_opy_ += str(platform[bstack1llllll11_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡒࡦࡳࡥࠨೈ")]) + bstack1llllll11_opy_ (u"ࠫ࠱ࠦࠧ೉")
    if bstack1llllll11_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ೊ") in platform:
      bstack11lllll1_opy_ += str(platform[bstack1llllll11_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡖࡦࡴࡶ࡭ࡴࡴࠧೋ")]) + bstack1llllll11_opy_ (u"ࠧ࠭ࠢࠪೌ")
  except Exception as e:
    logger.debug(bstack1llllll11_opy_ (u"ࠨࡕࡲࡱࡪࠦࡥࡳࡴࡲࡶࠥ࡯࡮ࠡࡩࡨࡲࡪࡸࡡࡵ࡫ࡱ࡫ࠥࡶ࡬ࡢࡶࡩࡳࡷࡳࠠࡴࡶࡵ࡭ࡳ࡭ࠠࡧࡱࡵࠤࡷ࡫ࡰࡰࡴࡷࠤ࡬࡫࡮ࡦࡴࡤࡸ࡮ࡵ࡮ࠨ್") + str(e))
  finally:
    if bstack11lllll1_opy_[len(bstack11lllll1_opy_) - 2:] == bstack1llllll11_opy_ (u"ࠩ࠯ࠤࠬ೎"):
      bstack11lllll1_opy_ = bstack11lllll1_opy_[:-2]
    return bstack11lllll1_opy_
def bstack1l11_opy_(path, bstack11lllll1_opy_):
  try:
    import xml.etree.ElementTree as ET
    bstack111l1l111_opy_ = ET.parse(path)
    bstack1llllll1_opy_ = bstack111l1l111_opy_.getroot()
    bstack1l1lllll_opy_ = None
    for suite in bstack1llllll1_opy_.iter(bstack1llllll11_opy_ (u"ࠪࡷࡺ࡯ࡴࡦࠩ೏")):
      if bstack1llllll11_opy_ (u"ࠫࡸࡵࡵࡳࡥࡨࠫ೐") in suite.attrib:
        suite.attrib[bstack1llllll11_opy_ (u"ࠬࡴࡡ࡮ࡧࠪ೑")] += bstack1llllll11_opy_ (u"࠭ࠠࠨ೒") + bstack11lllll1_opy_
        bstack1l1lllll_opy_ = suite
    bstack1l11lll1_opy_ = None
    for robot in bstack1llllll1_opy_.iter(bstack1llllll11_opy_ (u"ࠧࡳࡱࡥࡳࡹ࠭೓")):
      bstack1l11lll1_opy_ = robot
    bstack1llllll1l_opy_ = len(bstack1l11lll1_opy_.findall(bstack1llllll11_opy_ (u"ࠨࡵࡸ࡭ࡹ࡫ࠧ೔")))
    if bstack1llllll1l_opy_ == 1:
      bstack1l11lll1_opy_.remove(bstack1l11lll1_opy_.findall(bstack1llllll11_opy_ (u"ࠩࡶࡹ࡮ࡺࡥࠨೕ"))[0])
      bstack1lll1lll1_opy_ = ET.Element(bstack1llllll11_opy_ (u"ࠪࡷࡺ࡯ࡴࡦࠩೖ"), attrib={bstack1llllll11_opy_ (u"ࠫࡳࡧ࡭ࡦࠩ೗"):bstack1llllll11_opy_ (u"࡙ࠬࡵࡪࡶࡨࡷࠬ೘"), bstack1llllll11_opy_ (u"࠭ࡩࡥࠩ೙"):bstack1llllll11_opy_ (u"ࠧࡴ࠲ࠪ೚")})
      bstack1l11lll1_opy_.insert(1, bstack1lll1lll1_opy_)
      bstack1l1l11lll_opy_ = None
      for suite in bstack1l11lll1_opy_.iter(bstack1llllll11_opy_ (u"ࠨࡵࡸ࡭ࡹ࡫ࠧ೛")):
        bstack1l1l11lll_opy_ = suite
      bstack1l1l11lll_opy_.append(bstack1l1lllll_opy_)
      bstack11l11111l_opy_ = None
      for status in bstack1l1lllll_opy_.iter(bstack1llllll11_opy_ (u"ࠩࡶࡸࡦࡺࡵࡴࠩ೜")):
        bstack11l11111l_opy_ = status
      bstack1l1l11lll_opy_.append(bstack11l11111l_opy_)
    bstack111l1l111_opy_.write(path)
  except Exception as e:
    logger.debug(bstack1llllll11_opy_ (u"ࠪࡉࡷࡸ࡯ࡳࠢ࡬ࡲࠥࡶࡡࡳࡵ࡬ࡲ࡬ࠦࡷࡩ࡫࡯ࡩࠥ࡭ࡥ࡯ࡧࡵࡥࡹ࡯࡮ࡨࠢࡵࡳࡧࡵࡴࠡࡴࡨࡴࡴࡸࡴࠨೝ") + str(e))
def bstack11l11l11_opy_(outs_dir, pabot_args, options, start_time_string, tests_root_name):
  global bstack11lllll11_opy_
  global CONFIG
  if bstack1llllll11_opy_ (u"ࠦࡵࡿࡴࡩࡱࡱࡴࡦࡺࡨࠣೞ") in options:
    del options[bstack1llllll11_opy_ (u"ࠧࡶࡹࡵࡪࡲࡲࡵࡧࡴࡩࠤ೟")]
  bstack1l1l111_opy_ = bstack1111111l_opy_()
  for bstack1l1lll1ll_opy_ in bstack1l1l111_opy_.keys():
    path = os.path.join(os.getcwd(), bstack1llllll11_opy_ (u"࠭ࡰࡢࡤࡲࡸࡤࡸࡥࡴࡷ࡯ࡸࡸ࠭ೠ"), str(bstack1l1lll1ll_opy_), bstack1llllll11_opy_ (u"ࠧࡰࡷࡷࡴࡺࡺ࠮ࡹ࡯࡯ࠫೡ"))
    bstack1l11_opy_(path, bstack11111ll1_opy_(bstack1l1l111_opy_[bstack1l1lll1ll_opy_]))
  bstack1l11111ll_opy_()
  return bstack11lllll11_opy_(outs_dir, pabot_args, options, start_time_string, tests_root_name)
def bstack111l1lll_opy_(self, ff_profile_dir):
  global bstack11_opy_
  if not ff_profile_dir:
    return None
  return bstack11_opy_(self, ff_profile_dir)
def bstack1lllll1_opy_(datasources, opts_for_run, outs_dir, pabot_args, suite_group):
  from pabot.pabot import QueueItem
  global CONFIG
  global bstack11111l11_opy_
  bstack1l111llll_opy_ = []
  if bstack1llllll11_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫೢ") in CONFIG:
    bstack1l111llll_opy_ = CONFIG[bstack1llllll11_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬೣ")]
  return [
    QueueItem(
      datasources,
      outs_dir,
      opts_for_run,
      suite,
      pabot_args[bstack1llllll11_opy_ (u"ࠥࡧࡴࡳ࡭ࡢࡰࡧࠦ೤")],
      pabot_args[bstack1llllll11_opy_ (u"ࠦࡻ࡫ࡲࡣࡱࡶࡩࠧ೥")],
      argfile,
      pabot_args.get(bstack1llllll11_opy_ (u"ࠧ࡮ࡩࡷࡧࠥ೦")),
      pabot_args[bstack1llllll11_opy_ (u"ࠨࡰࡳࡱࡦࡩࡸࡹࡥࡴࠤ೧")],
      platform[0],
      bstack11111l11_opy_
    )
    for suite in suite_group
    for argfile in pabot_args[bstack1llllll11_opy_ (u"ࠢࡢࡴࡪࡹࡲ࡫࡮ࡵࡨ࡬ࡰࡪࡹࠢ೨")] or [(bstack1llllll11_opy_ (u"ࠣࠤ೩"), None)]
    for platform in enumerate(bstack1l111llll_opy_)
  ]
def bstack11lll1ll_opy_(self, datasources, outs_dir, options,
  execution_item, command, verbose, argfile,
  hive=None, processes=0,platform_index=0,bstack11ll1l_opy_=bstack1llllll11_opy_ (u"ࠩࠪ೪")):
  global bstack11llllll1_opy_
  self.platform_index = platform_index
  self.bstackl_opy_ = bstack11ll1l_opy_
  bstack11llllll1_opy_(self, datasources, outs_dir, options,
    execution_item, command, verbose, argfile, hive, processes)
def bstack11l111l1l_opy_(caller_id, datasources, is_last, item, outs_dir):
  global bstack11l1l111_opy_
  global bstack1l1l1l11l_opy_
  if not bstack1llllll11_opy_ (u"ࠪࡺࡦࡸࡩࡢࡤ࡯ࡩࠬ೫") in item.options:
    item.options[bstack1llllll11_opy_ (u"ࠫࡻࡧࡲࡪࡣࡥࡰࡪ࠭೬")] = []
  for v in item.options[bstack1llllll11_opy_ (u"ࠬࡼࡡࡳ࡫ࡤࡦࡱ࡫ࠧ೭")]:
    if bstack1llllll11_opy_ (u"࠭ࡂࡔࡖࡄࡇࡐࡖࡌࡂࡖࡉࡓࡗࡓࡉࡏࡆࡈ࡜ࠬ೮") in v:
      item.options[bstack1llllll11_opy_ (u"ࠧࡷࡣࡵ࡭ࡦࡨ࡬ࡦࠩ೯")].remove(v)
    if bstack1llllll11_opy_ (u"ࠨࡄࡖࡘࡆࡉࡋࡄࡎࡌࡅࡗࡍࡓࠨ೰") in v:
      item.options[bstack1llllll11_opy_ (u"ࠩࡹࡥࡷ࡯ࡡࡣ࡮ࡨࠫೱ")].remove(v)
  item.options[bstack1llllll11_opy_ (u"ࠪࡺࡦࡸࡩࡢࡤ࡯ࡩࠬೲ")].insert(0, bstack1llllll11_opy_ (u"ࠫࡇ࡙ࡔࡂࡅࡎࡔࡑࡇࡔࡇࡑࡕࡑࡎࡔࡄࡆ࡚࠽ࡿࢂ࠭ೳ").format(item.platform_index))
  item.options[bstack1llllll11_opy_ (u"ࠬࡼࡡࡳ࡫ࡤࡦࡱ࡫ࠧ೴")].insert(0, bstack1llllll11_opy_ (u"࠭ࡂࡔࡖࡄࡇࡐࡊࡅࡇࡎࡒࡇࡆࡒࡉࡅࡇࡑࡘࡎࡌࡉࡆࡔ࠽ࡿࢂ࠭೵").format(item.bstackl_opy_))
  if bstack1l1l1l11l_opy_:
    item.options[bstack1llllll11_opy_ (u"ࠧࡷࡣࡵ࡭ࡦࡨ࡬ࡦࠩ೶")].insert(0, bstack1llllll11_opy_ (u"ࠨࡄࡖࡘࡆࡉࡋࡄࡎࡌࡅࡗࡍࡓ࠻ࡽࢀࠫ೷").format(bstack1l1l1l11l_opy_))
  return bstack11l1l111_opy_(caller_id, datasources, is_last, item, outs_dir)
def bstack1ll1lll1_opy_(command, item_index):
  global bstack1l1l1l11l_opy_
  if bstack1l1l1l11l_opy_:
    command[0] = command[0].replace(bstack1llllll11_opy_ (u"ࠩࡵࡳࡧࡵࡴࠨ೸"), bstack1llllll11_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠯ࡶࡨࡰࠦࡲࡰࡤࡲࡸ࠲࡯࡮ࡵࡧࡵࡲࡦࡲࠠ࠮࠯ࡥࡷࡹࡧࡣ࡬ࡡ࡬ࡸࡪࡳ࡟ࡪࡰࡧࡩࡽࠦࠧ೹") + str(item_index) + bstack1llllll11_opy_ (u"ࠫࠥ࠭೺") + bstack1l1l1l11l_opy_, 1)
  else:
    command[0] = command[0].replace(bstack1llllll11_opy_ (u"ࠬࡸ࡯ࡣࡱࡷࠫ೻"), bstack1llllll11_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠲ࡹࡤ࡬ࠢࡵࡳࡧࡵࡴ࠮࡫ࡱࡸࡪࡸ࡮ࡢ࡮ࠣ࠱࠲ࡨࡳࡵࡣࡦ࡯ࡤ࡯ࡴࡦ࡯ࡢ࡭ࡳࡪࡥࡹࠢࠪ೼") + str(item_index), 1)
def bstack1ll1l111l_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index):
  global bstack1l111l1l_opy_
  bstack1ll1lll1_opy_(command, item_index)
  return bstack1l111l1l_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index)
def bstack1l11l11l1_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir):
  global bstack1l111l1l_opy_
  bstack1ll1lll1_opy_(command, item_index)
  return bstack1l111l1l_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir)
def bstack1l1llll_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout):
  global bstack1l111l1l_opy_
  bstack1ll1lll1_opy_(command, item_index)
  return bstack1l111l1l_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout)
def bstack111llllll_opy_(self, runner, quiet=False, capture=True):
  global bstack1111111_opy_
  bstack1ll1l1111_opy_ = bstack1111111_opy_(self, runner, quiet=False, capture=True)
  if self.exception:
    if not hasattr(runner, bstack1llllll11_opy_ (u"ࠧࡦࡺࡦࡩࡵࡺࡩࡰࡰࡢࡥࡷࡸࠧ೽")):
      runner.exception_arr = []
    if not hasattr(runner, bstack1llllll11_opy_ (u"ࠨࡧࡻࡧࡤࡺࡲࡢࡥࡨࡦࡦࡩ࡫ࡠࡣࡵࡶࠬ೾")):
      runner.exc_traceback_arr = []
    runner.exception = self.exception
    runner.exc_traceback = self.exc_traceback
    runner.exception_arr.append(self.exception)
    runner.exc_traceback_arr.append(self.exc_traceback)
  return bstack1ll1l1111_opy_
def bstack1ll111ll1_opy_(self, name, context, *args):
  global bstack1111ll1l_opy_
  if name in [bstack1llllll11_opy_ (u"ࠩࡥࡩ࡫ࡵࡲࡦࡡࡩࡩࡦࡺࡵࡳࡧࠪ೿"), bstack1llllll11_opy_ (u"ࠪࡦࡪ࡬࡯ࡳࡧࡢࡷࡨ࡫࡮ࡢࡴ࡬ࡳࠬഀ")]:
    bstack1111ll1l_opy_(self, name, context, *args)
  if name == bstack1llllll11_opy_ (u"ࠫࡧ࡫ࡦࡰࡴࡨࡣ࡫࡫ࡡࡵࡷࡵࡩࠬഁ"):
    try:
      if(not bstack1llll1l11_opy_):
        bstack1l11ll1ll_opy_ = str(self.feature.name)
        bstack1ll1ll11_opy_(context, bstack1l11ll1ll_opy_)
        context.browser.execute_script(bstack1llllll11_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࠤࡤࡧࡹ࡯࡯࡯ࠤ࠽ࠤࠧࡹࡥࡵࡕࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪࠨࠬࠡࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧࡀࠠࡼࠤࡱࡥࡲ࡫ࠢ࠻ࠢࠪം") + json.dumps(bstack1l11ll1ll_opy_) + bstack1llllll11_opy_ (u"࠭ࡽࡾࠩഃ"))
      self.driver_before_scenario = False
    except Exception as e:
      logger.debug(bstack1llllll11_opy_ (u"ࠧࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡷࡪࡺࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠡࡰࡤࡱࡪࠦࡩ࡯ࠢࡥࡩ࡫ࡵࡲࡦࠢࡩࡩࡦࡺࡵࡳࡧ࠽ࠤࢀࢃࠧഄ").format(str(e)))
  if name == bstack1llllll11_opy_ (u"ࠨࡤࡨࡪࡴࡸࡥࡠࡵࡦࡩࡳࡧࡲࡪࡱࠪഅ"):
    try:
      if not hasattr(self, bstack1llllll11_opy_ (u"ࠩࡧࡶ࡮ࡼࡥࡳࡡࡥࡩ࡫ࡵࡲࡦࡡࡶࡧࡪࡴࡡࡳ࡫ࡲࠫആ")):
        self.driver_before_scenario = True
      if(not bstack1llll1l11_opy_):
        scenario_name = args[0].name
        feature_name = bstack1l11ll1ll_opy_ = str(self.feature.name)
        bstack1l11ll1ll_opy_ = feature_name + bstack1llllll11_opy_ (u"ࠪࠤ࠲ࠦࠧഇ") + scenario_name
        if self.driver_before_scenario:
          bstack1ll1ll11_opy_(context, bstack1l11ll1ll_opy_)
          context.browser.execute_script(bstack1llllll11_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࡻࠣࡣࡦࡸ࡮ࡵ࡮ࠣ࠼ࠣࠦࡸ࡫ࡴࡔࡧࡶࡷ࡮ࡵ࡮ࡏࡣࡰࡩࠧ࠲ࠠࠣࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠦ࠿ࠦࡻࠣࡰࡤࡱࡪࠨ࠺ࠡࠩഈ") + json.dumps(bstack1l11ll1ll_opy_) + bstack1llllll11_opy_ (u"ࠬࢃࡽࠨഉ"))
    except Exception as e:
      logger.debug(bstack1llllll11_opy_ (u"࠭ࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡶࡩࡹࠦࡳࡦࡵࡶ࡭ࡴࡴࠠ࡯ࡣࡰࡩࠥ࡯࡮ࠡࡤࡨࡪࡴࡸࡥࠡࡵࡦࡩࡳࡧࡲࡪࡱ࠽ࠤࢀࢃࠧഊ").format(str(e)))
  if name == bstack1llllll11_opy_ (u"ࠧࡢࡨࡷࡩࡷࡥࡳࡤࡧࡱࡥࡷ࡯࡯ࠨഋ"):
    try:
      bstack1l1l111l_opy_ = args[0].status.name
      if str(bstack1l1l111l_opy_).lower() == bstack1llllll11_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨഌ"):
        bstack1l1111lll_opy_ = bstack1llllll11_opy_ (u"ࠩࠪ഍")
        bstack111l_opy_ = bstack1llllll11_opy_ (u"ࠪࠫഎ")
        bstack1l11l1l_opy_ = bstack1llllll11_opy_ (u"ࠫࠬഏ")
        try:
          import traceback
          bstack1l1111lll_opy_ = self.exception.__class__.__name__
          bstack1lll1111l_opy_ = traceback.format_tb(self.exc_traceback)
          bstack111l_opy_ = bstack1llllll11_opy_ (u"ࠬࠦࠧഐ").join(bstack1lll1111l_opy_)
          bstack1l11l1l_opy_ = bstack1lll1111l_opy_[-1]
        except Exception as e:
          logger.debug(bstack1l1l1l1l1_opy_.format(str(e)))
        bstack1l1111lll_opy_ += bstack1l11l1l_opy_
        bstack11l11111_opy_(context, json.dumps(str(args[0].name) + bstack1llllll11_opy_ (u"ࠨࠠ࠮ࠢࡉࡥ࡮ࡲࡥࡥࠣ࡟ࡲࠧ഑") + str(bstack111l_opy_)), bstack1llllll11_opy_ (u"ࠢࡦࡴࡵࡳࡷࠨഒ"))
        if self.driver_before_scenario:
          bstack1llll1lll_opy_(context, bstack1llllll11_opy_ (u"ࠣࡨࡤ࡭ࡱ࡫ࡤࠣഓ"), bstack1l1111lll_opy_)
        context.browser.execute_script(bstack1llllll11_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࢀࠨࡡࡤࡶ࡬ࡳࡳࠨ࠺ࠡࠤࡤࡲࡳࡵࡴࡢࡶࡨࠦ࠱ࠦࠢࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠥ࠾ࠥࢁࠢࡥࡣࡷࡥࠧࡀࠧഔ") + json.dumps(str(args[0].name) + bstack1llllll11_opy_ (u"ࠥࠤ࠲ࠦࡆࡢ࡫࡯ࡩࡩࠧ࡜࡯ࠤക") + str(bstack111l_opy_)) + bstack1llllll11_opy_ (u"ࠫ࠱ࠦࠢ࡭ࡧࡹࡩࡱࠨ࠺ࠡࠤࡨࡶࡷࡵࡲࠣࡿࢀࠫഖ"))
        if self.driver_before_scenario:
          context.browser.execute_script(bstack1llllll11_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࠤࡤࡧࡹ࡯࡯࡯ࠤ࠽ࠤࠧࡹࡥࡵࡕࡨࡷࡸ࡯࡯࡯ࡕࡷࡥࡹࡻࡳࠣ࠮ࠣࠦࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠢ࠻ࠢࡾࠦࡸࡺࡡࡵࡷࡶࠦ࠿ࠨࡦࡢ࡫࡯ࡩࡩࠨࠬࠡࠤࡵࡩࡦࡹ࡯࡯ࠤ࠽ࠤࠬഗ") + json.dumps(bstack1llllll11_opy_ (u"ࠨࡓࡤࡧࡱࡥࡷ࡯࡯ࠡࡨࡤ࡭ࡱ࡫ࡤࠡࡹ࡬ࡸ࡭ࡀࠠ࡝ࡰࠥഘ") + str(bstack1l1111lll_opy_)) + bstack1llllll11_opy_ (u"ࠧࡾࡿࠪങ"))
      else:
        bstack11l11111_opy_(context, bstack1llllll11_opy_ (u"ࠣࡒࡤࡷࡸ࡫ࡤࠢࠤച"), bstack1llllll11_opy_ (u"ࠤ࡬ࡲ࡫ࡵࠢഛ"))
        if self.driver_before_scenario:
          bstack1llll1lll_opy_(context, bstack1llllll11_opy_ (u"ࠥࡴࡦࡹࡳࡦࡦࠥജ"))
        context.browser.execute_script(bstack1llllll11_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࡻࠣࡣࡦࡸ࡮ࡵ࡮ࠣ࠼ࠣࠦࡦࡴ࡮ࡰࡶࡤࡸࡪࠨࠬࠡࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧࡀࠠࡼࠤࡧࡥࡹࡧࠢ࠻ࠩഝ") + json.dumps(str(args[0].name) + bstack1llllll11_opy_ (u"ࠧࠦ࠭ࠡࡒࡤࡷࡸ࡫ࡤࠢࠤഞ")) + bstack1llllll11_opy_ (u"࠭ࠬࠡࠤ࡯ࡩࡻ࡫࡬ࠣ࠼ࠣࠦ࡮ࡴࡦࡰࠤࢀࢁࠬട"))
        if self.driver_before_scenario:
          context.browser.execute_script(bstack1llllll11_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࠦࡦࡩࡴࡪࡱࡱࠦ࠿ࠦࠢࡴࡧࡷࡗࡪࡹࡳࡪࡱࡱࡗࡹࡧࡴࡶࡵࠥ࠰ࠥࠨࡡࡳࡩࡸࡱࡪࡴࡴࡴࠤ࠽ࠤࢀࠨࡳࡵࡣࡷࡹࡸࠨ࠺ࠣࡲࡤࡷࡸ࡫ࡤࠣࡿࢀࠫഠ"))
    except Exception as e:
      logger.debug(bstack1llllll11_opy_ (u"ࠨࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡲࡧࡲ࡬ࠢࡶࡩࡸࡹࡩࡰࡰࠣࡷࡹࡧࡴࡶࡵࠣ࡭ࡳࠦࡡࡧࡶࡨࡶࠥ࡬ࡥࡢࡶࡸࡶࡪࡀࠠࡼࡿࠪഡ").format(str(e)))
  if name == bstack1llllll11_opy_ (u"ࠩࡤࡪࡹ࡫ࡲࡠࡨࡨࡥࡹࡻࡲࡦࠩഢ"):
    try:
      if context.failed is True:
        bstack111111l1_opy_ = []
        bstack111ll111_opy_ = []
        bstack11llll1l_opy_ = []
        bstack111ll1l1l_opy_ = bstack1llllll11_opy_ (u"ࠪࠫണ")
        try:
          import traceback
          for exc in self.exception_arr:
            bstack111111l1_opy_.append(exc.__class__.__name__)
          for exc_tb in self.exc_traceback_arr:
            bstack1lll1111l_opy_ = traceback.format_tb(exc_tb)
            bstack11l11l1l1_opy_ = bstack1llllll11_opy_ (u"ࠫࠥ࠭ത").join(bstack1lll1111l_opy_)
            bstack111ll111_opy_.append(bstack11l11l1l1_opy_)
            bstack11llll1l_opy_.append(bstack1lll1111l_opy_[-1])
        except Exception as e:
          logger.debug(bstack1l1l1l1l1_opy_.format(str(e)))
        bstack1l1111lll_opy_ = bstack1llllll11_opy_ (u"ࠬ࠭ഥ")
        for i in range(len(bstack111111l1_opy_)):
          bstack1l1111lll_opy_ += bstack111111l1_opy_[i] + bstack11llll1l_opy_[i] + bstack1llllll11_opy_ (u"࠭࡜࡯ࠩദ")
        bstack111ll1l1l_opy_ = bstack1llllll11_opy_ (u"ࠧࠡࠩധ").join(bstack111ll111_opy_)
        if not self.driver_before_scenario:
          bstack11l11111_opy_(context, bstack111ll1l1l_opy_, bstack1llllll11_opy_ (u"ࠣࡧࡵࡶࡴࡸࠢന"))
          bstack1llll1lll_opy_(context, bstack1llllll11_opy_ (u"ࠤࡩࡥ࡮ࡲࡥࡥࠤഩ"), bstack1l1111lll_opy_)
          context.browser.execute_script(bstack1llllll11_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࢁࠢࡢࡥࡷ࡭ࡴࡴࠢ࠻ࠢࠥࡥࡳࡴ࡯ࡵࡣࡷࡩࠧ࠲ࠠࠣࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠦ࠿ࠦࡻࠣࡦࡤࡸࡦࠨ࠺ࠨപ") + json.dumps(bstack111ll1l1l_opy_) + bstack1llllll11_opy_ (u"ࠫ࠱ࠦࠢ࡭ࡧࡹࡩࡱࠨ࠺ࠡࠤࡨࡶࡷࡵࡲࠣࡿࢀࠫഫ"))
          context.browser.execute_script(bstack1llllll11_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࠤࡤࡧࡹ࡯࡯࡯ࠤ࠽ࠤࠧࡹࡥࡵࡕࡨࡷࡸ࡯࡯࡯ࡕࡷࡥࡹࡻࡳࠣ࠮ࠣࠦࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠢ࠻ࠢࡾࠦࡸࡺࡡࡵࡷࡶࠦ࠿ࠨࡦࡢ࡫࡯ࡩࡩࠨࠬࠡࠤࡵࡩࡦࡹ࡯࡯ࠤ࠽ࠤࠬബ") + json.dumps(bstack1llllll11_opy_ (u"ࠨࡓࡰ࡯ࡨࠤࡸࡩࡥ࡯ࡣࡵ࡭ࡴࡹࠠࡧࡣ࡬ࡰࡪࡪ࠺ࠡ࡞ࡱࠦഭ") + str(bstack1l1111lll_opy_)) + bstack1llllll11_opy_ (u"ࠧࡾࡿࠪമ"))
      else:
        if not self.driver_before_scenario:
          bstack11l11111_opy_(context, bstack1llllll11_opy_ (u"ࠣࡈࡨࡥࡹࡻࡲࡦ࠼ࠣࠦയ") + str(self.feature.name) + bstack1llllll11_opy_ (u"ࠤࠣࡴࡦࡹࡳࡦࡦࠤࠦര"), bstack1llllll11_opy_ (u"ࠥ࡭ࡳ࡬࡯ࠣറ"))
          bstack1llll1lll_opy_(context, bstack1llllll11_opy_ (u"ࠦࡵࡧࡳࡴࡧࡧࠦല"))
          context.browser.execute_script(bstack1llllll11_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࠤࡤࡧࡹ࡯࡯࡯ࠤ࠽ࠤࠧࡧ࡮࡯ࡱࡷࡥࡹ࡫ࠢ࠭ࠢࠥࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸࠨ࠺ࠡࡽࠥࡨࡦࡺࡡࠣ࠼ࠪള") + json.dumps(bstack1llllll11_opy_ (u"ࠨࡆࡦࡣࡷࡹࡷ࡫࠺ࠡࠤഴ") + str(self.feature.name) + bstack1llllll11_opy_ (u"ࠢࠡࡲࡤࡷࡸ࡫ࡤࠢࠤവ")) + bstack1llllll11_opy_ (u"ࠨ࠮ࠣࠦࡱ࡫ࡶࡦ࡮ࠥ࠾ࠥࠨࡩ࡯ࡨࡲࠦࢂࢃࠧശ"))
          context.browser.execute_script(bstack1llllll11_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࢀࠨࡡࡤࡶ࡬ࡳࡳࠨ࠺ࠡࠤࡶࡩࡹ࡙ࡥࡴࡵ࡬ࡳࡳ࡙ࡴࡢࡶࡸࡷࠧ࠲ࠠࠣࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠦ࠿ࠦࡻࠣࡵࡷࡥࡹࡻࡳࠣ࠼ࠥࡴࡦࡹࡳࡦࡦࠥࢁࢂ࠭ഷ"))
    except Exception as e:
      logger.debug(bstack1llllll11_opy_ (u"ࠪࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦ࡭ࡢࡴ࡮ࠤࡸ࡫ࡳࡴ࡫ࡲࡲࠥࡹࡴࡢࡶࡸࡷࠥ࡯࡮ࠡࡣࡩࡸࡪࡸࠠࡧࡧࡤࡸࡺࡸࡥ࠻ࠢࡾࢁࠬസ").format(str(e)))
  if name in [bstack1llllll11_opy_ (u"ࠫࡦ࡬ࡴࡦࡴࡢࡪࡪࡧࡴࡶࡴࡨࠫഹ"), bstack1llllll11_opy_ (u"ࠬࡧࡦࡵࡧࡵࡣࡸࡩࡥ࡯ࡣࡵ࡭ࡴ࠭ഺ")]:
    bstack1111ll1l_opy_(self, name, context, *args)
    if (name == bstack1llllll11_opy_ (u"࠭ࡡࡧࡶࡨࡶࡤࡹࡣࡦࡰࡤࡶ࡮ࡵ഻ࠧ") and self.driver_before_scenario) or (name == bstack1llllll11_opy_ (u"ࠧࡢࡨࡷࡩࡷࡥࡦࡦࡣࡷࡹࡷ࡫഼ࠧ") and not self.driver_before_scenario):
      try:
        context.browser.quit()
      except Exception:
        pass
def bstack1ll1111_opy_(config, startdir):
  return bstack1llllll11_opy_ (u"ࠣࡦࡵ࡭ࡻ࡫ࡲ࠻ࠢࡾ࠴ࢂࠨഽ").format(bstack1llllll11_opy_ (u"ࠤࡅࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࠣാ"))
class Notset:
  def __repr__(self):
    return bstack1llllll11_opy_ (u"ࠥࡀࡓࡕࡔࡔࡇࡗࡂࠧി")
notset = Notset()
def bstack111lllll1_opy_(self, name: str, default=notset, skip: bool = False):
  global bstack1ll11l1_opy_
  if str(name).lower() == bstack1llllll11_opy_ (u"ࠫࡩࡸࡩࡷࡧࡵࠫീ"):
    return bstack1llllll11_opy_ (u"ࠧࡈࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࠦു")
  else:
    return bstack1ll11l1_opy_(self, name, default, skip)
def bstack111l1l1_opy_(item, when):
  global bstack11ll11l1l_opy_
  try:
    bstack11ll11l1l_opy_(item, when)
  except Exception as e:
    pass
def bstack11lll1l_opy_():
  return
def bstack111l1l1ll_opy_(type, name, status, reason, bstack1lllllll1_opy_, bstack1l1ll1_opy_):
  bstack11l1l11l1_opy_ = {
    bstack1llllll11_opy_ (u"࠭ࡡࡤࡶ࡬ࡳࡳ࠭ൂ"): type,
    bstack1llllll11_opy_ (u"ࠧࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠪൃ"): {}
  }
  if type == bstack1llllll11_opy_ (u"ࠨࡣࡱࡲࡴࡺࡡࡵࡧࠪൄ"):
    bstack11l1l11l1_opy_[bstack1llllll11_opy_ (u"ࠩࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠬ൅")][bstack1llllll11_opy_ (u"ࠪࡰࡪࡼࡥ࡭ࠩെ")] = bstack1lllllll1_opy_
    bstack11l1l11l1_opy_[bstack1llllll11_opy_ (u"ࠫࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠧേ")][bstack1llllll11_opy_ (u"ࠬࡪࡡࡵࡣࠪൈ")] = json.dumps(str(bstack1l1ll1_opy_))
  if type == bstack1llllll11_opy_ (u"࠭ࡳࡦࡶࡖࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧ൉"):
    bstack11l1l11l1_opy_[bstack1llllll11_opy_ (u"ࠧࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠪൊ")][bstack1llllll11_opy_ (u"ࠨࡰࡤࡱࡪ࠭ോ")] = name
  if type == bstack1llllll11_opy_ (u"ࠩࡶࡩࡹ࡙ࡥࡴࡵ࡬ࡳࡳ࡙ࡴࡢࡶࡸࡷࠬൌ"):
    bstack11l1l11l1_opy_[bstack1llllll11_opy_ (u"ࠪࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸ്࠭")][bstack1llllll11_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫൎ")] = status
    if status == bstack1llllll11_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬ൏"):
      bstack11l1l11l1_opy_[bstack1llllll11_opy_ (u"࠭ࡡࡳࡩࡸࡱࡪࡴࡴࡴࠩ൐")][bstack1llllll11_opy_ (u"ࠧࡳࡧࡤࡷࡴࡴࠧ൑")] = json.dumps(str(reason))
  bstack11l11ll1_opy_ = bstack1llllll11_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࢂ࠭൒").format(json.dumps(bstack11l1l11l1_opy_))
  return bstack11l11ll1_opy_
def bstack11l1l1l_opy_(item, call, rep):
  global bstack1llll11ll_opy_
  global bstack1lll1ll1l_opy_
  name = bstack1llllll11_opy_ (u"ࠩࠪ൓")
  try:
    if rep.when == bstack1llllll11_opy_ (u"ࠪࡧࡦࡲ࡬ࠨൔ"):
      bstack1ll11l11_opy_ = threading.current_thread().bstack1l1l11_opy_
      try:
        name = str(rep.nodeid)
        bstack1lllll1l_opy_ = bstack111l1l1ll_opy_(bstack1llllll11_opy_ (u"ࠫࡸ࡫ࡴࡔࡧࡶࡷ࡮ࡵ࡮ࡏࡣࡰࡩࠬൕ"), name, bstack1llllll11_opy_ (u"ࠬ࠭ൖ"), bstack1llllll11_opy_ (u"࠭ࠧൗ"), bstack1llllll11_opy_ (u"ࠧࠨ൘"), bstack1llllll11_opy_ (u"ࠨࠩ൙"))
        for driver in bstack1lll1ll1l_opy_:
          if bstack1ll11l11_opy_ == driver.session_id:
            driver.execute_script(bstack1lllll1l_opy_)
      except Exception as e:
        logger.debug(bstack1llllll11_opy_ (u"ࠩࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡸ࡫ࡴࡵ࡫ࡱ࡫ࠥࡹࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠣࡪࡴࡸࠠࡱࡻࡷࡩࡸࡺ࠭ࡣࡦࡧࠤࡸ࡫ࡳࡴ࡫ࡲࡲ࠿ࠦࡻࡾࠩ൚").format(str(e)))
      try:
        status = bstack1llllll11_opy_ (u"ࠪࡪࡦ࡯࡬ࡦࡦࠪ൛") if rep.outcome.lower() == bstack1llllll11_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡧࡧࠫ൜") else bstack1llllll11_opy_ (u"ࠬࡶࡡࡴࡵࡨࡨࠬ൝")
        reason = bstack1llllll11_opy_ (u"࠭ࠧ൞")
        if (reason != bstack1llllll11_opy_ (u"ࠢࠣൟ")):
          try:
            if (threading.current_thread().bstackTestErrorMessages == None):
                threading.current_thread().bstackTestErrorMessages = []
          except Exception as e:
            threading.current_thread().bstackTestErrorMessages = []
          threading.current_thread().bstackTestErrorMessages.append(str(reason))
        if status == bstack1llllll11_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨൠ"):
          reason = rep.longrepr.reprcrash.message
          if (not threading.current_thread().bstackTestErrorMessages):
            threading.current_thread().bstackTestErrorMessages = []
          threading.current_thread().bstackTestErrorMessages.append(reason)
        level = bstack1llllll11_opy_ (u"ࠩ࡬ࡲ࡫ࡵࠧൡ") if status == bstack1llllll11_opy_ (u"ࠪࡴࡦࡹࡳࡦࡦࠪൢ") else bstack1llllll11_opy_ (u"ࠫࡪࡸࡲࡰࡴࠪൣ")
        data = name + bstack1llllll11_opy_ (u"ࠬࠦࡰࡢࡵࡶࡩࡩࠧࠧ൤") if status == bstack1llllll11_opy_ (u"࠭ࡰࡢࡵࡶࡩࡩ࠭൥") else name + bstack1llllll11_opy_ (u"ࠧࠡࡨࡤ࡭ࡱ࡫ࡤࠢࠢࠪ൦") + reason
        bstack1ll11_opy_ = bstack111l1l1ll_opy_(bstack1llllll11_opy_ (u"ࠨࡣࡱࡲࡴࡺࡡࡵࡧࠪ൧"), bstack1llllll11_opy_ (u"ࠩࠪ൨"), bstack1llllll11_opy_ (u"ࠪࠫ൩"), bstack1llllll11_opy_ (u"ࠫࠬ൪"), level, data)
        for driver in bstack1lll1ll1l_opy_:
          if bstack1ll11l11_opy_ == driver.session_id:
            driver.execute_script(bstack1ll11_opy_)
      except Exception as e:
        logger.debug(bstack1llllll11_opy_ (u"ࠬࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡴࡧࡷࡸ࡮ࡴࡧࠡࡵࡨࡷࡸ࡯࡯࡯ࠢࡦࡳࡳࡺࡥࡹࡶࠣࡪࡴࡸࠠࡱࡻࡷࡩࡸࡺ࠭ࡣࡦࡧࠤࡸ࡫ࡳࡴ࡫ࡲࡲ࠿ࠦࡻࡾࠩ൫").format(str(e)))
  except Exception as e:
    logger.debug(bstack1llllll11_opy_ (u"࠭ࡅࡳࡴࡲࡶࠥ࡯࡮ࠡࡩࡨࡸࡹ࡯࡮ࡨࠢࡶࡸࡦࡺࡥࠡ࡫ࡱࠤࡵࡿࡴࡦࡵࡷ࠱ࡧࡪࡤࠡࡶࡨࡷࡹࠦࡳࡵࡣࡷࡹࡸࡀࠠࡼࡿࠪ൬").format(str(e)))
  bstack1llll11ll_opy_(item, call, rep)
def bstack11llll1ll_opy_(framework_name):
  global bstack1l1l1l_opy_
  global bstack1l111111l_opy_
  global bstack1ll1lll1l_opy_
  bstack1l1l1l_opy_ = framework_name
  logger.info(bstack1ll1l11ll_opy_.format(bstack1l1l1l_opy_.split(bstack1llllll11_opy_ (u"ࠧ࠮ࠩ൭"))[0]))
  try:
    from selenium import webdriver
    from selenium.webdriver.common.service import Service
    from selenium.webdriver.remote.webdriver import WebDriver
    Service.start = bstack1l1ll11_opy_
    Service.stop = bstack111l11ll_opy_
    webdriver.Remote.__init__ = bstack1111lll11_opy_
    webdriver.Remote.get = bstack111l1l1l1_opy_
    WebDriver.close = bstack1llll111_opy_
    WebDriver.quit = bstack1lll1_opy_
    bstack1l111111l_opy_ = True
  except Exception as e:
    pass
  bstack1llll111l_opy_()
  if not bstack1l111111l_opy_:
    bstack1ll1_opy_(bstack1llllll11_opy_ (u"ࠣࡒࡤࡧࡰࡧࡧࡦࡵࠣࡲࡴࡺࠠࡪࡰࡶࡸࡦࡲ࡬ࡦࡦࠥ൮"), bstack11111l1l_opy_)
  if bstack11ll1111l_opy_():
    try:
      from selenium.webdriver.remote.remote_connection import RemoteConnection
      RemoteConnection._get_proxy_url = bstack1llllllll_opy_
    except Exception as e:
      logger.error(bstack11l1111l1_opy_.format(str(e)))
  if (bstack1llllll11_opy_ (u"ࠩࡵࡳࡧࡵࡴࠨ൯") in str(framework_name).lower()):
    try:
      from robot import run_cli
      from robot.output import Output
      from robot.running.status import TestStatus
      from pabot.pabot import QueueItem
      from pabot import pabot
      try:
        from SeleniumLibrary.keywords.webdrivertools.webdrivertools import WebDriverCreator
        WebDriverCreator._get_ff_profile = bstack111l1lll_opy_
        from SeleniumLibrary.keywords.webdrivertools.webdrivertools import WebDriverCache
        WebDriverCache.close = bstack11l1lll1l_opy_
      except Exception as e:
        logger.warn(bstack1ll1111ll_opy_ + str(e))
      try:
        from AppiumLibrary.utils.applicationcache import ApplicationCache
        ApplicationCache.close = bstack1111l1l1_opy_
      except Exception as e:
        logger.debug(bstack11llll_opy_ + str(e))
    except Exception as e:
      bstack1ll1_opy_(e, bstack1ll1111ll_opy_)
    Output.end_test = bstack11111l_opy_
    TestStatus.__init__ = bstack11l11ll11_opy_
    QueueItem.__init__ = bstack11lll1ll_opy_
    pabot._create_items = bstack1lllll1_opy_
    try:
      from pabot import __version__ as bstack11l111l1_opy_
      if version.parse(bstack11l111l1_opy_) >= version.parse(bstack1llllll11_opy_ (u"ࠪ࠶࠳࠷࠵࠯࠲ࠪ൰")):
        pabot._run = bstack1l1llll_opy_
      elif version.parse(bstack11l111l1_opy_) >= version.parse(bstack1llllll11_opy_ (u"ࠫ࠷࠴࠱࠴࠰࠳ࠫ൱")):
        pabot._run = bstack1l11l11l1_opy_
      else:
        pabot._run = bstack1ll1l111l_opy_
    except Exception as e:
      pabot._run = bstack1ll1l111l_opy_
    pabot._create_command_for_execution = bstack11l111l1l_opy_
    pabot._report_results = bstack11l11l11_opy_
  if bstack1llllll11_opy_ (u"ࠬࡨࡥࡩࡣࡹࡩࠬ൲") in str(framework_name).lower():
    try:
      from behave.runner import Runner
      from behave.model import Step
    except Exception as e:
      bstack1ll1_opy_(e, bstack11ll111_opy_)
    Runner.run_hook = bstack1ll111ll1_opy_
    Step.run = bstack111llllll_opy_
  if bstack1llllll11_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠭൳") in str(framework_name).lower():
    try:
      from pytest_selenium import pytest_selenium
      from _pytest.config import Config
      pytest_selenium.pytest_report_header = bstack1ll1111_opy_
      from pytest_selenium.drivers import browserstack
      browserstack.pytest_selenium_runtest_makereport = bstack11lll1l_opy_
      Config.getoption = bstack111lllll1_opy_
    except Exception as e:
      pass
    try:
      from _pytest import runner
      runner._update_current_test_var = bstack111l1l1_opy_
    except Exception as e:
      pass
    try:
      from pytest_bdd import reporting
      reporting.runtest_makereport = bstack11l1l1l_opy_
    except Exception as e:
      pass
def bstack11llll1_opy_():
  global CONFIG
  if bstack1llllll11_opy_ (u"ࠧࡱࡣࡵࡥࡱࡲࡥ࡭ࡵࡓࡩࡷࡖ࡬ࡢࡶࡩࡳࡷࡳࠧ൴") in CONFIG and int(CONFIG[bstack1llllll11_opy_ (u"ࠨࡲࡤࡶࡦࡲ࡬ࡦ࡮ࡶࡔࡪࡸࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨ൵")]) > 1:
    logger.warn(bstack1l11l1ll1_opy_)
def bstack11l1111l_opy_(arg):
  arg.append(bstack1llllll11_opy_ (u"ࠤ࠰࠱࡮ࡳࡰࡰࡴࡷ࠱ࡲࡵࡤࡦ࠿࡬ࡱࡵࡵࡲࡵ࡮࡬ࡦࠧ൶"))
  arg.append(bstack1llllll11_opy_ (u"ࠥ࠱࡜ࠨ൷"))
  arg.append(bstack1llllll11_opy_ (u"ࠦ࡮࡭࡮ࡰࡴࡨ࠾ࡒࡵࡤࡶ࡮ࡨࠤࡦࡲࡲࡦࡣࡧࡽࠥ࡯࡭ࡱࡱࡵࡸࡪࡪ࠺ࡱࡻࡷࡩࡸࡺ࠮ࡑࡻࡷࡩࡸࡺࡗࡢࡴࡱ࡭ࡳ࡭ࠢ൸"))
  arg.append(bstack1llllll11_opy_ (u"ࠧ࠳ࡗࠣ൹"))
  arg.append(bstack1llllll11_opy_ (u"ࠨࡩࡨࡰࡲࡶࡪࡀࡔࡩࡧࠣ࡬ࡴࡵ࡫ࡪ࡯ࡳࡰࠧൺ"))
  global CONFIG
  bstack11llll1ll_opy_(bstack111ll11_opy_)
  os.environ[bstack1llllll11_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡕࡔࡇࡕࡒࡆࡓࡅࠨൻ")] = CONFIG[bstack1llllll11_opy_ (u"ࠨࡷࡶࡩࡷࡔࡡ࡮ࡧࠪർ")]
  os.environ[bstack1llllll11_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡃࡆࡇࡊ࡙ࡓࡠࡍࡈ࡝ࠬൽ")] = CONFIG[bstack1llllll11_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵࡎࡩࡾ࠭ൾ")]
  from _pytest.config import main as bstack1lll11l11_opy_
  bstack1lll11l11_opy_(arg)
def bstack1111_opy_(arg):
  bstack11llll1ll_opy_(bstack1ll1ll111_opy_)
  from behave.__main__ import main as bstack11l1ll11l_opy_
  bstack11l1ll11l_opy_(arg)
def bstack11lll1l11_opy_():
  logger.info(bstack1l11111l1_opy_)
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument(bstack1llllll11_opy_ (u"ࠫࡸ࡫ࡴࡶࡲࠪൿ"), help=bstack1llllll11_opy_ (u"ࠬࡍࡥ࡯ࡧࡵࡥࡹ࡫ࠠࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࠦࡣࡰࡰࡩ࡭࡬࠭඀"))
  parser.add_argument(bstack1llllll11_opy_ (u"࠭࠭ࡶࠩඁ"), bstack1llllll11_opy_ (u"ࠧ࠮࠯ࡸࡷࡪࡸ࡮ࡢ࡯ࡨࠫං"), help=bstack1llllll11_opy_ (u"ࠨ࡛ࡲࡹࡷࠦࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠥࡻࡳࡦࡴࡱࡥࡲ࡫ࠧඃ"))
  parser.add_argument(bstack1llllll11_opy_ (u"ࠩ࠰࡯ࠬ඄"), bstack1llllll11_opy_ (u"ࠪ࠱࠲ࡱࡥࡺࠩඅ"), help=bstack1llllll11_opy_ (u"ࠫ࡞ࡵࡵࡳࠢࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠡࡣࡦࡧࡪࡹࡳࠡ࡭ࡨࡽࠬආ"))
  parser.add_argument(bstack1llllll11_opy_ (u"ࠬ࠳ࡦࠨඇ"), bstack1llllll11_opy_ (u"࠭࠭࠮ࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࠫඈ"), help=bstack1llllll11_opy_ (u"࡚ࠧࡱࡸࡶࠥࡺࡥࡴࡶࠣࡪࡷࡧ࡭ࡦࡹࡲࡶࡰ࠭ඉ"))
  bstack1ll1l1_opy_ = parser.parse_args()
  try:
    bstack11ll111ll_opy_ = bstack1llllll11_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡨࡧࡱࡩࡷ࡯ࡣ࠯ࡻࡰࡰ࠳ࡹࡡ࡮ࡲ࡯ࡩࠬඊ")
    if bstack1ll1l1_opy_.framework and bstack1ll1l1_opy_.framework not in (bstack1llllll11_opy_ (u"ࠩࡳࡽࡹ࡮࡯࡯ࠩඋ"), bstack1llllll11_opy_ (u"ࠪࡴࡾࡺࡨࡰࡰ࠶ࠫඌ")):
      bstack11ll111ll_opy_ = bstack1llllll11_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡪࡷࡧ࡭ࡦࡹࡲࡶࡰ࠴ࡹ࡮࡮࠱ࡷࡦࡳࡰ࡭ࡧࠪඍ")
    bstack1l11l1_opy_ = os.path.join(os.path.dirname(os.path.realpath(__file__)), bstack11ll111ll_opy_)
    bstack1ll_opy_ = open(bstack1l11l1_opy_, bstack1llllll11_opy_ (u"ࠬࡸࠧඎ"))
    bstack11llll11_opy_ = bstack1ll_opy_.read()
    bstack1ll_opy_.close()
    if bstack1ll1l1_opy_.username:
      bstack11llll11_opy_ = bstack11llll11_opy_.replace(bstack1llllll11_opy_ (u"࡙࠭ࡐࡗࡕࡣ࡚࡙ࡅࡓࡐࡄࡑࡊ࠭ඏ"), bstack1ll1l1_opy_.username)
    if bstack1ll1l1_opy_.key:
      bstack11llll11_opy_ = bstack11llll11_opy_.replace(bstack1llllll11_opy_ (u"࡚ࠧࡑࡘࡖࡤࡇࡃࡄࡇࡖࡗࡤࡑࡅ࡚ࠩඐ"), bstack1ll1l1_opy_.key)
    if bstack1ll1l1_opy_.framework:
      bstack11llll11_opy_ = bstack11llll11_opy_.replace(bstack1llllll11_opy_ (u"ࠨ࡛ࡒ࡙ࡗࡥࡆࡓࡃࡐࡉ࡜ࡕࡒࡌࠩඑ"), bstack1ll1l1_opy_.framework)
    file_name = bstack1llllll11_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡻࡰࡰࠬඒ")
    file_path = os.path.abspath(file_name)
    bstack1l1llll1_opy_ = open(file_path, bstack1llllll11_opy_ (u"ࠪࡻࠬඓ"))
    bstack1l1llll1_opy_.write(bstack11llll11_opy_)
    bstack1l1llll1_opy_.close()
    logger.info(bstack111111l_opy_)
    try:
      os.environ[bstack1llllll11_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡊࡗࡇࡍࡆ࡙ࡒࡖࡐ࠭ඔ")] = bstack1ll1l1_opy_.framework if bstack1ll1l1_opy_.framework != None else bstack1llllll11_opy_ (u"ࠧࠨඕ")
      config = yaml.safe_load(bstack11llll11_opy_)
      config[bstack1llllll11_opy_ (u"࠭ࡳࡰࡷࡵࡧࡪ࠭ඖ")] = bstack1llllll11_opy_ (u"ࠧࡱࡻࡷ࡬ࡴࡴ࠭ࡴࡧࡷࡹࡵ࠭඗")
      bstack11lll1lll_opy_(bstack1111ll_opy_, config)
    except Exception as e:
      logger.debug(bstack1l111l1_opy_.format(str(e)))
  except Exception as e:
    logger.error(bstack1ll1l1l11_opy_.format(str(e)))
def bstack11lll1lll_opy_(bstack111ll111l_opy_, config, bstack1ll1ll_opy_ = {}):
  global bstack1llll1ll1_opy_
  if not config:
    return
  bstack11l11ll_opy_ = bstack1l1l11ll_opy_ if not bstack1llll1ll1_opy_ else ( bstack11lll11ll_opy_ if bstack1llllll11_opy_ (u"ࠨࡣࡳࡴࠬ඘") in config else bstack1l11ll11_opy_ )
  data = {
    bstack1llllll11_opy_ (u"ࠩࡸࡷࡪࡸࡎࡢ࡯ࡨࠫ඙"): config[bstack1llllll11_opy_ (u"ࠪࡹࡸ࡫ࡲࡏࡣࡰࡩࠬක")],
    bstack1llllll11_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶࡏࡪࡿࠧඛ"): config[bstack1llllll11_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷࡐ࡫ࡹࠨග")],
    bstack1llllll11_opy_ (u"࠭ࡥࡷࡧࡱࡸࡤࡺࡹࡱࡧࠪඝ"): bstack111ll111l_opy_,
    bstack1llllll11_opy_ (u"ࠧࡦࡸࡨࡲࡹࡥࡰࡳࡱࡳࡩࡷࡺࡩࡦࡵࠪඞ"): {
      bstack1llllll11_opy_ (u"ࠨ࡮ࡤࡲ࡬ࡻࡡࡨࡧࡢࡪࡷࡧ࡭ࡦࡹࡲࡶࡰ࠭ඟ"): str(config[bstack1llllll11_opy_ (u"ࠩࡶࡳࡺࡸࡣࡦࠩච")]) if bstack1llllll11_opy_ (u"ࠪࡷࡴࡻࡲࡤࡧࠪඡ") in config else bstack1llllll11_opy_ (u"ࠦࡺࡴ࡫࡯ࡱࡺࡲࠧජ"),
      bstack1llllll11_opy_ (u"ࠬࡸࡥࡧࡧࡵࡶࡪࡸࠧඣ"): bstack1l1l1ll1l_opy_(os.getenv(bstack1llllll11_opy_ (u"ࠨࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡌࡒࡂࡏࡈ࡛ࡔࡘࡋࠣඤ"), bstack1llllll11_opy_ (u"ࠢࠣඥ"))),
      bstack1llllll11_opy_ (u"ࠨ࡮ࡤࡲ࡬ࡻࡡࡨࡧࠪඦ"): bstack1llllll11_opy_ (u"ࠩࡳࡽࡹ࡮࡯࡯ࠩට"),
      bstack1llllll11_opy_ (u"ࠪࡴࡷࡵࡤࡶࡥࡷࠫඨ"): bstack11l11ll_opy_,
      bstack1llllll11_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠧඩ"): config[bstack1llllll11_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡒࡦࡳࡥࠨඪ")]if config[bstack1llllll11_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦࠩණ")] else bstack1llllll11_opy_ (u"ࠢࡶࡰ࡮ࡲࡴࡽ࡮ࠣඬ"),
      bstack1llllll11_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪත"): str(config[bstack1llllll11_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫථ")]) if bstack1llllll11_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬද") in config else bstack1llllll11_opy_ (u"ࠦࡺࡴ࡫࡯ࡱࡺࡲࠧධ"),
      bstack1llllll11_opy_ (u"ࠬࡵࡳࠨන"): sys.platform,
      bstack1llllll11_opy_ (u"࠭ࡨࡰࡵࡷࡲࡦࡳࡥࠨ඲"): socket.gethostname()
    }
  }
  update(data[bstack1llllll11_opy_ (u"ࠧࡦࡸࡨࡲࡹࡥࡰࡳࡱࡳࡩࡷࡺࡩࡦࡵࠪඳ")], bstack1ll1ll_opy_)
  try:
    response = bstack111ll_opy_(bstack1llllll11_opy_ (u"ࠨࡒࡒࡗ࡙࠭ප"), bstack1l1ll1l_opy_, data, config)
    if response:
      logger.debug(bstack1lll1111_opy_.format(bstack111ll111l_opy_, str(response.json())))
  except Exception as e:
    logger.debug(bstack1l1llll11_opy_.format(str(e)))
def bstack111ll_opy_(type, url, data, config):
  bstack1l1l11l1l_opy_ = bstack111ll11l_opy_.format(url)
  proxies = bstack1lll1l1l1_opy_(config, bstack1l1l11l1l_opy_)
  if type == bstack1llllll11_opy_ (u"ࠩࡓࡓࡘ࡚ࠧඵ"):
    response = requests.post(bstack1l1l11l1l_opy_, json=data,
                    headers={bstack1llllll11_opy_ (u"ࠪࡇࡴࡴࡴࡦࡰࡷ࠱࡙ࡿࡰࡦࠩබ"): bstack1llllll11_opy_ (u"ࠫࡦࡶࡰ࡭࡫ࡦࡥࡹ࡯࡯࡯࠱࡭ࡷࡴࡴࠧභ")}, auth=(config[bstack1llllll11_opy_ (u"ࠬࡻࡳࡦࡴࡑࡥࡲ࡫ࠧම")], config[bstack1llllll11_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸࡑࡥࡺࠩඹ")]), proxies=proxies)
  return response
def bstack1l1l1ll1l_opy_(framework):
  return bstack1llllll11_opy_ (u"ࠢࡼࡿ࠰ࡴࡾࡺࡨࡰࡰࡤ࡫ࡪࡴࡴ࠰ࡽࢀࠦය").format(str(framework), __version__) if framework else bstack1llllll11_opy_ (u"ࠣࡲࡼࡸ࡭ࡵ࡮ࡢࡩࡨࡲࡹ࠵ࡻࡾࠤර").format(__version__)
def bstack111l11ll1_opy_():
  global CONFIG
  if bool(CONFIG):
    return
  try:
    bstack11lllllll_opy_()
    logger.debug(bstack1l1llllll_opy_.format(str(CONFIG)))
    bstack11l1l1ll1_opy_()
    bstack11ll1ll11_opy_()
  except Exception as e:
    logger.error(bstack1llllll11_opy_ (u"ࠤࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡹࡥࡵࡷࡳ࠰ࠥ࡫ࡲࡳࡱࡵ࠾ࠥࠨ඼") + str(e))
    sys.exit(1)
  sys.excepthook = bstack11lll1l1_opy_
  atexit.register(bstack1lll111_opy_)
  signal.signal(signal.SIGINT, bstack1l11lll1l_opy_)
  signal.signal(signal.SIGTERM, bstack1l11lll1l_opy_)
def bstack11lll1l1_opy_(exctype, value, traceback):
  global bstack1lll1ll1l_opy_
  try:
    for driver in bstack1lll1ll1l_opy_:
      driver.execute_script(
        bstack1llllll11_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࢁࠢࡢࡥࡷ࡭ࡴࡴࠢ࠻ࠢࠥࡷࡪࡺࡓࡦࡵࡶ࡭ࡴࡴࡓࡵࡣࡷࡹࡸࠨࠬࠡࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧࡀࠠࡼࠤࡶࡸࡦࡺࡵࡴࠤ࠽ࠦ࡫ࡧࡩ࡭ࡧࡧࠦ࠱ࠦࠢࡳࡧࡤࡷࡴࡴࠢ࠻ࠢࠪල") + json.dumps(bstack1llllll11_opy_ (u"ࠦࡘ࡫ࡳࡴ࡫ࡲࡲࠥ࡬ࡡࡪ࡮ࡨࡨࠥࡽࡩࡵࡪ࠽ࠤࡡࡴࠢ඾") + str(value)) + bstack1llllll11_opy_ (u"ࠬࢃࡽࠨ඿"))
  except Exception:
    pass
  bstack1lllll11_opy_(value)
  sys.__excepthook__(exctype, value, traceback)
  sys.exit(1)
def bstack1lllll11_opy_(message = bstack1llllll11_opy_ (u"࠭ࠧව")):
  global CONFIG
  try:
    if message:
      bstack1ll1ll_opy_ = {
        bstack1llllll11_opy_ (u"ࠧࡦࡴࡵࡳࡷ࠭ශ"): str(message)
      }
      bstack11lll1lll_opy_(bstack1l11l1lll_opy_, CONFIG, bstack1ll1ll_opy_)
    else:
      bstack11lll1lll_opy_(bstack1l11l1lll_opy_, CONFIG)
  except Exception as e:
    logger.debug(bstack1111l1_opy_.format(str(e)))
def bstack1ll1l11_opy_(bstack1llll1l1l_opy_, size):
  bstack1lll11lll_opy_ = []
  while len(bstack1llll1l1l_opy_) > size:
    bstack11l1lll_opy_ = bstack1llll1l1l_opy_[:size]
    bstack1lll11lll_opy_.append(bstack11l1lll_opy_)
    bstack1llll1l1l_opy_   = bstack1llll1l1l_opy_[size:]
  bstack1lll11lll_opy_.append(bstack1llll1l1l_opy_)
  return bstack1lll11lll_opy_
def bstack111lll1l1_opy_(args):
  if bstack1llllll11_opy_ (u"ࠨ࠯ࡰࠫෂ") in args and bstack1llllll11_opy_ (u"ࠩࡳࡨࡧ࠭ස") in args:
    return True
  return False
def run_on_browserstack(bstack1l111l1ll_opy_=None, bstack1ll1111l_opy_=None, bstack11l1llll1_opy_=False):
  global CONFIG
  global bstack1l1111ll1_opy_
  global bstack111ll1ll1_opy_
  bstack11ll1l1ll_opy_ = bstack1llllll11_opy_ (u"ࠪࠫහ")
  if bstack1l111l1ll_opy_ and isinstance(bstack1l111l1ll_opy_, str):
    bstack1l111l1ll_opy_ = eval(bstack1l111l1ll_opy_)
  if bstack1l111l1ll_opy_:
    CONFIG = bstack1l111l1ll_opy_[bstack1llllll11_opy_ (u"ࠫࡈࡕࡎࡇࡋࡊࠫළ")]
    bstack1l1111ll1_opy_ = bstack1l111l1ll_opy_[bstack1llllll11_opy_ (u"ࠬࡎࡕࡃࡡࡘࡖࡑ࠭ෆ")]
    bstack111ll1ll1_opy_ = bstack1l111l1ll_opy_[bstack1llllll11_opy_ (u"࠭ࡉࡔࡡࡄࡔࡕࡥࡁࡖࡖࡒࡑࡆ࡚ࡅࠨ෇")]
    bstack11ll1l1ll_opy_ = bstack1llllll11_opy_ (u"ࠧࡱࡻࡷ࡬ࡴࡴࠧ෈")
  if not bstack11l1llll1_opy_:
    if len(sys.argv) <= 1:
      logger.critical(bstack11l11ll1l_opy_)
      return
    if sys.argv[1] == bstack1llllll11_opy_ (u"ࠨ࠯࠰ࡺࡪࡸࡳࡪࡱࡱࠫ෉")  or sys.argv[1] == bstack1llllll11_opy_ (u"ࠩ࠰ࡺ්ࠬ"):
      logger.info(bstack1llllll11_opy_ (u"ࠪࡆࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠢࡓࡽࡹ࡮࡯࡯ࠢࡖࡈࡐࠦࡶࡼࡿࠪ෋").format(__version__))
      return
    if sys.argv[1] == bstack1llllll11_opy_ (u"ࠫࡸ࡫ࡴࡶࡲࠪ෌"):
      bstack11lll1l11_opy_()
      return
  args = sys.argv
  bstack111l11ll1_opy_()
  global bstack1ll11l111_opy_
  global bstack11l11lll1_opy_
  global bstack1l11l1111_opy_
  global bstack1111lll1l_opy_
  global bstack11111l11_opy_
  global bstack1l1l1l11l_opy_
  global bstack11l11l11l_opy_
  global bstack1ll1lll1l_opy_
  if not bstack11ll1l1ll_opy_:
    if args[1] == bstack1llllll11_opy_ (u"ࠬࡶࡹࡵࡪࡲࡲࠬ෍") or args[1] == bstack1llllll11_opy_ (u"࠭ࡰࡺࡶ࡫ࡳࡳ࠹ࠧ෎"):
      bstack11ll1l1ll_opy_ = bstack1llllll11_opy_ (u"ࠧࡱࡻࡷ࡬ࡴࡴࠧා")
      args = args[2:]
    elif args[1] == bstack1llllll11_opy_ (u"ࠨࡴࡲࡦࡴࡺࠧැ"):
      bstack11ll1l1ll_opy_ = bstack1llllll11_opy_ (u"ࠩࡵࡳࡧࡵࡴࠨෑ")
      args = args[2:]
    elif args[1] == bstack1llllll11_opy_ (u"ࠪࡴࡦࡨ࡯ࡵࠩි"):
      bstack11ll1l1ll_opy_ = bstack1llllll11_opy_ (u"ࠫࡵࡧࡢࡰࡶࠪී")
      args = args[2:]
    elif args[1] == bstack1llllll11_opy_ (u"ࠬࡸ࡯ࡣࡱࡷ࠱࡮ࡴࡴࡦࡴࡱࡥࡱ࠭ු"):
      bstack11ll1l1ll_opy_ = bstack1llllll11_opy_ (u"࠭ࡲࡰࡤࡲࡸ࠲࡯࡮ࡵࡧࡵࡲࡦࡲࠧ෕")
      args = args[2:]
    elif args[1] == bstack1llllll11_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺࠧූ"):
      bstack11ll1l1ll_opy_ = bstack1llllll11_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࠨ෗")
      args = args[2:]
    elif args[1] == bstack1llllll11_opy_ (u"ࠩࡥࡩ࡭ࡧࡶࡦࠩෘ"):
      bstack11ll1l1ll_opy_ = bstack1llllll11_opy_ (u"ࠪࡦࡪ࡮ࡡࡷࡧࠪෙ")
      args = args[2:]
    else:
      if not bstack1llllll11_opy_ (u"ࠫ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࠧේ") in CONFIG or str(CONFIG[bstack1llllll11_opy_ (u"ࠬ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࠨෛ")]).lower() in [bstack1llllll11_opy_ (u"࠭ࡰࡺࡶ࡫ࡳࡳ࠭ො"), bstack1llllll11_opy_ (u"ࠧࡱࡻࡷ࡬ࡴࡴ࠳ࠨෝ")]:
        bstack11ll1l1ll_opy_ = bstack1llllll11_opy_ (u"ࠨࡲࡼࡸ࡭ࡵ࡮ࠨෞ")
        args = args[1:]
      elif str(CONFIG[bstack1llllll11_opy_ (u"ࠩࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࠬෟ")]).lower() == bstack1llllll11_opy_ (u"ࠪࡶࡴࡨ࡯ࡵࠩ෠"):
        bstack11ll1l1ll_opy_ = bstack1llllll11_opy_ (u"ࠫࡷࡵࡢࡰࡶࠪ෡")
        args = args[1:]
      elif str(CONFIG[bstack1llllll11_opy_ (u"ࠬ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࠨ෢")]).lower() == bstack1llllll11_opy_ (u"࠭ࡰࡢࡤࡲࡸࠬ෣"):
        bstack11ll1l1ll_opy_ = bstack1llllll11_opy_ (u"ࠧࡱࡣࡥࡳࡹ࠭෤")
        args = args[1:]
      elif str(CONFIG[bstack1llllll11_opy_ (u"ࠨࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࠫ෥")]).lower() == bstack1llllll11_opy_ (u"ࠩࡳࡽࡹ࡫ࡳࡵࠩ෦"):
        bstack11ll1l1ll_opy_ = bstack1llllll11_opy_ (u"ࠪࡴࡾࡺࡥࡴࡶࠪ෧")
        args = args[1:]
      elif str(CONFIG[bstack1llllll11_opy_ (u"ࠫ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࠧ෨")]).lower() == bstack1llllll11_opy_ (u"ࠬࡨࡥࡩࡣࡹࡩࠬ෩"):
        bstack11ll1l1ll_opy_ = bstack1llllll11_opy_ (u"࠭ࡢࡦࡪࡤࡺࡪ࠭෪")
        args = args[1:]
      else:
        os.environ[bstack1llllll11_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡆࡓࡃࡐࡉ࡜ࡕࡒࡌࠩ෫")] = bstack11ll1l1ll_opy_
        bstack1l1lll1_opy_(bstack1lllll1ll_opy_)
  global bstack11ll1l1_opy_
  if bstack1l111l1ll_opy_:
    try:
      os.environ[bstack1llllll11_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡇࡔࡄࡑࡊ࡝ࡏࡓࡍࠪ෬")] = bstack11ll1l1ll_opy_
      bstack11lll1lll_opy_(bstack1l1l1ll1_opy_, CONFIG)
    except Exception as e:
      logger.debug(bstack1111l1_opy_.format(str(e)))
  global bstack1llll1l_opy_
  global bstack1ll11ll_opy_
  global bstack11111_opy_
  global bstack11l111l11_opy_
  global bstack1l111l111_opy_
  global bstack11l1ll1l1_opy_
  global bstack11_opy_
  global bstack1l111l1l_opy_
  global bstack11llllll1_opy_
  global bstack11l1l111_opy_
  global bstack111l1111_opy_
  global bstack1111ll1l_opy_
  global bstack1111111_opy_
  global bstack1llll1l1_opy_
  global bstack11l1ll1_opy_
  global bstack1ll11l1_opy_
  global bstack11ll11l1l_opy_
  global bstack11lllll11_opy_
  global bstack1llll11ll_opy_
  try:
    from selenium import webdriver
    from selenium.webdriver.remote.webdriver import WebDriver
    bstack1llll1l_opy_ = webdriver.Remote.__init__
    bstack1ll11ll_opy_ = WebDriver.quit
    bstack111l1111_opy_ = WebDriver.close
    bstack1llll1l1_opy_ = WebDriver.get
  except Exception as e:
    pass
  try:
    import Browser
    from subprocess import Popen
    bstack11ll1l1_opy_ = Popen.__init__
  except Exception as e:
    pass
  if bstack1l11ll1l_opy_():
    if bstack1l11l111l_opy_() < version.parse(bstack1l1l1l1l_opy_):
      logger.error(bstack11llll11l_opy_.format(bstack1l11l111l_opy_()))
    else:
      try:
        from selenium.webdriver.remote.remote_connection import RemoteConnection
        bstack11l1ll1_opy_ = RemoteConnection._get_proxy_url
      except Exception as e:
        logger.error(bstack11l1111l1_opy_.format(str(e)))
  if bstack11ll1l1ll_opy_ != bstack1llllll11_opy_ (u"ࠩࡳࡽࡹ࡮࡯࡯ࠩ෭") or (bstack11ll1l1ll_opy_ == bstack1llllll11_opy_ (u"ࠪࡴࡾࡺࡨࡰࡰࠪ෮") and not bstack1l111l1ll_opy_):
    bstack1l1ll1ll1_opy_()
  if (bstack11ll1l1ll_opy_ in [bstack1llllll11_opy_ (u"ࠫࡵࡧࡢࡰࡶࠪ෯"), bstack1llllll11_opy_ (u"ࠬࡸ࡯ࡣࡱࡷࠫ෰"), bstack1llllll11_opy_ (u"࠭ࡲࡰࡤࡲࡸ࠲࡯࡮ࡵࡧࡵࡲࡦࡲࠧ෱")]):
    try:
      from robot import run_cli
      from robot.output import Output
      from robot.running.status import TestStatus
      from pabot.pabot import QueueItem
      from pabot import pabot
      try:
        from SeleniumLibrary.keywords.webdrivertools.webdrivertools import WebDriverCreator
        from SeleniumLibrary.keywords.webdrivertools.webdrivertools import WebDriverCache
        WebDriverCreator._get_ff_profile = bstack111l1lll_opy_
        bstack1l111l111_opy_ = WebDriverCache.close
      except Exception as e:
        logger.warn(bstack1ll1111ll_opy_ + str(e))
      try:
        from AppiumLibrary.utils.applicationcache import ApplicationCache
        bstack11l111l11_opy_ = ApplicationCache.close
      except Exception as e:
        logger.debug(bstack11llll_opy_ + str(e))
    except Exception as e:
      bstack1ll1_opy_(e, bstack1ll1111ll_opy_)
    if bstack11ll1l1ll_opy_ != bstack1llllll11_opy_ (u"ࠧࡳࡱࡥࡳࡹ࠳ࡩ࡯ࡶࡨࡶࡳࡧ࡬ࠨෲ"):
      bstack1l11111ll_opy_()
    bstack11111_opy_ = Output.end_test
    bstack11l1ll1l1_opy_ = TestStatus.__init__
    bstack1l111l1l_opy_ = pabot._run
    bstack11llllll1_opy_ = QueueItem.__init__
    bstack11l1l111_opy_ = pabot._create_command_for_execution
    bstack11lllll11_opy_ = pabot._report_results
  if bstack11ll1l1ll_opy_ == bstack1llllll11_opy_ (u"ࠨࡤࡨ࡬ࡦࡼࡥࠨෳ"):
    try:
      from behave.runner import Runner
      from behave.model import Step
    except Exception as e:
      bstack1ll1_opy_(e, bstack11ll111_opy_)
    bstack1111ll1l_opy_ = Runner.run_hook
    bstack1111111_opy_ = Step.run
  if bstack11ll1l1ll_opy_ == bstack1llllll11_opy_ (u"ࠩࡳࡽࡹ࡫ࡳࡵࠩ෴"):
    try:
      from _pytest.config import Config
      bstack1ll11l1_opy_ = Config.getoption
      from _pytest import runner
      bstack11ll11l1l_opy_ = runner._update_current_test_var
    except Exception as e:
      logger.warn(e, bstack11ll1ll1l_opy_)
    try:
      from pytest_bdd import reporting
      bstack1llll11ll_opy_ = reporting.runtest_makereport
    except Exception as e:
      logger.debug(bstack1llllll11_opy_ (u"ࠪࡔࡱ࡫ࡡࡴࡧࠣ࡭ࡳࡹࡴࡢ࡮࡯ࠤࡵࡿࡴࡦࡵࡷ࠱ࡧࡪࡤࠡࡶࡲࠤࡷࡻ࡮ࠡࡲࡼࡸࡪࡹࡴ࠮ࡤࡧࡨࠥࡺࡥࡴࡶࡶࠫ෵"))
  if bstack11ll1l1ll_opy_ == bstack1llllll11_opy_ (u"ࠫࡵࡿࡴࡩࡱࡱࠫ෶"):
    bstack11l11lll1_opy_ = True
    if bstack1l111l1ll_opy_ and bstack11l1llll1_opy_:
      bstack11111l11_opy_ = CONFIG.get(bstack1llllll11_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴࠩ෷"), {}).get(bstack1llllll11_opy_ (u"࠭࡬ࡰࡥࡤࡰࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨ෸"))
      bstack11llll1ll_opy_(bstack11ll11l1_opy_)
    elif bstack1l111l1ll_opy_:
      bstack11111l11_opy_ = CONFIG.get(bstack1llllll11_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࡓࡵࡺࡩࡰࡰࡶࠫ෹"), {}).get(bstack1llllll11_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪ෺"))
      global bstack1lll1ll1l_opy_
      try:
        if bstack111lll1l1_opy_(bstack1l111l1ll_opy_[bstack1llllll11_opy_ (u"ࠩࡩ࡭ࡱ࡫࡟࡯ࡣࡰࡩࠬ෻")]) and multiprocessing.current_process().name == bstack1llllll11_opy_ (u"ࠪ࠴ࠬ෼"):
          bstack1l111l1ll_opy_[bstack1llllll11_opy_ (u"ࠫ࡫࡯࡬ࡦࡡࡱࡥࡲ࡫ࠧ෽")].remove(bstack1llllll11_opy_ (u"ࠬ࠳࡭ࠨ෾"))
          bstack1l111l1ll_opy_[bstack1llllll11_opy_ (u"࠭ࡦࡪ࡮ࡨࡣࡳࡧ࡭ࡦࠩ෿")].remove(bstack1llllll11_opy_ (u"ࠧࡱࡦࡥࠫ฀"))
          bstack1l111l1ll_opy_[bstack1llllll11_opy_ (u"ࠨࡨ࡬ࡰࡪࡥ࡮ࡢ࡯ࡨࠫก")] = bstack1l111l1ll_opy_[bstack1llllll11_opy_ (u"ࠩࡩ࡭ࡱ࡫࡟࡯ࡣࡰࡩࠬข")][0]
          with open(bstack1l111l1ll_opy_[bstack1llllll11_opy_ (u"ࠪࡪ࡮ࡲࡥࡠࡰࡤࡱࡪ࠭ฃ")], bstack1llllll11_opy_ (u"ࠫࡷ࠭ค")) as f:
            bstack11l111ll1_opy_ = f.read()
          bstack1ll111l_opy_ = bstack1llllll11_opy_ (u"ࠧࠨࠢࡧࡴࡲࡱࠥࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡸࡪ࡫ࠡ࡫ࡰࡴࡴࡸࡴࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡪࡰ࡬ࡸ࡮ࡧ࡬ࡪࡼࡨ࠿ࠥࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣ࡮ࡴࡩࡵ࡫ࡤࡰ࡮ࢀࡥࠩࡽࢀ࠭ࡀࠦࡦࡳࡱࡰࠤࡵࡪࡢࠡ࡫ࡰࡴࡴࡸࡴࠡࡒࡧࡦࡀࠦ࡯ࡨࡡࡧࡦࠥࡃࠠࡑࡦࡥ࠲ࡩࡵ࡟ࡣࡴࡨࡥࡰࡁࠊࡥࡧࡩࠤࡲࡵࡤࡠࡤࡵࡩࡦࡱࠨࡴࡧ࡯ࡪ࠱ࠦࡡࡳࡩ࠯ࠤࡹ࡫࡭ࡱࡱࡵࡥࡷࡿࠠ࠾ࠢ࠳࠭࠿ࠐࠠࠡࡶࡵࡽ࠿ࠐࠠࠡࠢࠣࡥࡷ࡭ࠠ࠾ࠢࡶࡸࡷ࠮ࡩ࡯ࡶࠫࡥࡷ࡭ࠩࠬ࠳࠳࠭ࠏࠦࠠࡦࡺࡦࡩࡵࡺࠠࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣࡥࡸࠦࡥ࠻ࠌࠣࠤࠥࠦࡰࡢࡵࡶࠎࠥࠦ࡯ࡨࡡࡧࡦ࠭ࡹࡥ࡭ࡨ࠯ࡥࡷ࡭ࠬࡵࡧࡰࡴࡴࡸࡡࡳࡻࠬࠎࡕࡪࡢ࠯ࡦࡲࡣࡧࠦ࠽ࠡ࡯ࡲࡨࡤࡨࡲࡦࡣ࡮ࠎࡕࡪࡢ࠯ࡦࡲࡣࡧࡸࡥࡢ࡭ࠣࡁࠥࡳ࡯ࡥࡡࡥࡶࡪࡧ࡫ࠋࡒࡧࡦ࠭࠯࠮ࡴࡧࡷࡣࡹࡸࡡࡤࡧࠫ࠭ࡡࡴࠢࠣࠤฅ").format(str(bstack1l111l1ll_opy_))
          bstack11ll11_opy_ = bstack1ll111l_opy_ + bstack11l111ll1_opy_
          bstack11ll11111_opy_ = bstack1l111l1ll_opy_[bstack1llllll11_opy_ (u"࠭ࡦࡪ࡮ࡨࡣࡳࡧ࡭ࡦࠩฆ")] + bstack1llllll11_opy_ (u"ࠧࡠࡤࡶࡸࡦࡩ࡫ࡠࡶࡨࡱࡵ࠴ࡰࡺࠩง")
          with open(bstack11ll11111_opy_, bstack1llllll11_opy_ (u"ࠨࡹࠪจ")):
            pass
          with open(bstack11ll11111_opy_, bstack1llllll11_opy_ (u"ࠤࡺ࠯ࠧฉ")) as f:
            f.write(bstack11ll11_opy_)
          import subprocess
          bstack11ll1_opy_ = subprocess.run([bstack1llllll11_opy_ (u"ࠥࡴࡾࡺࡨࡰࡰࠥช"), bstack11ll11111_opy_])
          if os.path.exists(bstack11ll11111_opy_):
            os.unlink(bstack11ll11111_opy_)
          os._exit(bstack11ll1_opy_.returncode)
        else:
          if bstack111lll1l1_opy_(bstack1l111l1ll_opy_[bstack1llllll11_opy_ (u"ࠫ࡫࡯࡬ࡦࡡࡱࡥࡲ࡫ࠧซ")]):
            bstack1l111l1ll_opy_[bstack1llllll11_opy_ (u"ࠬ࡬ࡩ࡭ࡧࡢࡲࡦࡳࡥࠨฌ")].remove(bstack1llllll11_opy_ (u"࠭࠭࡮ࠩญ"))
            bstack1l111l1ll_opy_[bstack1llllll11_opy_ (u"ࠧࡧ࡫࡯ࡩࡤࡴࡡ࡮ࡧࠪฎ")].remove(bstack1llllll11_opy_ (u"ࠨࡲࡧࡦࠬฏ"))
            bstack1l111l1ll_opy_[bstack1llllll11_opy_ (u"ࠩࡩ࡭ࡱ࡫࡟࡯ࡣࡰࡩࠬฐ")] = bstack1l111l1ll_opy_[bstack1llllll11_opy_ (u"ࠪࡪ࡮ࡲࡥࡠࡰࡤࡱࡪ࠭ฑ")][0]
          bstack11llll1ll_opy_(bstack11ll11l1_opy_)
          sys.path.append(os.path.dirname(os.path.abspath(bstack1l111l1ll_opy_[bstack1llllll11_opy_ (u"ࠫ࡫࡯࡬ࡦࡡࡱࡥࡲ࡫ࠧฒ")])))
          sys.argv = sys.argv[2:]
          mod_globals = globals()
          mod_globals[bstack1llllll11_opy_ (u"ࠬࡥ࡟࡯ࡣࡰࡩࡤࡥࠧณ")] = bstack1llllll11_opy_ (u"࠭࡟ࡠ࡯ࡤ࡭ࡳࡥ࡟ࠨด")
          mod_globals[bstack1llllll11_opy_ (u"ࠧࡠࡡࡩ࡭ࡱ࡫࡟ࡠࠩต")] = os.path.abspath(bstack1l111l1ll_opy_[bstack1llllll11_opy_ (u"ࠨࡨ࡬ࡰࡪࡥ࡮ࡢ࡯ࡨࠫถ")])
          exec(open(bstack1l111l1ll_opy_[bstack1llllll11_opy_ (u"ࠩࡩ࡭ࡱ࡫࡟࡯ࡣࡰࡩࠬท")]).read(), mod_globals)
      except BaseException as e:
        try:
          traceback.print_exc()
          logger.error(bstack1llllll11_opy_ (u"ࠪࡇࡦࡻࡧࡩࡶࠣࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࡀࠠࡼࡿࠪธ").format(str(e)))
          for driver in bstack1lll1ll1l_opy_:
            bstack1ll1111l_opy_.append({
              bstack1llllll11_opy_ (u"ࠫࡳࡧ࡭ࡦࠩน"): bstack1l111l1ll_opy_[bstack1llllll11_opy_ (u"ࠬ࡬ࡩ࡭ࡧࡢࡲࡦࡳࡥࠨบ")],
              bstack1llllll11_opy_ (u"࠭ࡥࡳࡴࡲࡶࠬป"): str(e),
              bstack1llllll11_opy_ (u"ࠧࡪࡰࡧࡩࡽ࠭ผ"): multiprocessing.current_process().name
            })
            driver.execute_script(
              bstack1llllll11_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࠧࡧࡣࡵ࡫ࡲࡲࠧࡀࠠࠣࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡘࡺࡡࡵࡷࡶࠦ࠱ࠦࠢࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠥ࠾ࠥࢁࠢࡴࡶࡤࡸࡺࡹࠢ࠻ࠤࡩࡥ࡮ࡲࡥࡥࠤ࠯ࠤࠧࡸࡥࡢࡵࡲࡲࠧࡀࠠࠨฝ") + json.dumps(bstack1llllll11_opy_ (u"ࠤࡖࡩࡸࡹࡩࡰࡰࠣࡪࡦ࡯࡬ࡦࡦࠣࡻ࡮ࡺࡨ࠻ࠢ࡟ࡲࠧพ") + str(e)) + bstack1llllll11_opy_ (u"ࠪࢁࢂ࠭ฟ"))
        except Exception:
          pass
      finally:
        try:
          for driver in bstack1lll1ll1l_opy_:
            driver.quit()
        except Exception as e:
          pass
    else:
      bstack1ll1l1ll_opy_()
      bstack11llll1_opy_()
      bstack1ll1l1l1_opy_ = {
        bstack1llllll11_opy_ (u"ࠫ࡫࡯࡬ࡦࡡࡱࡥࡲ࡫ࠧภ"): args[0],
        bstack1llllll11_opy_ (u"ࠬࡉࡏࡏࡈࡌࡋࠬม"): CONFIG,
        bstack1llllll11_opy_ (u"࠭ࡈࡖࡄࡢ࡙ࡗࡒࠧย"): bstack1l1111ll1_opy_,
        bstack1llllll11_opy_ (u"ࠧࡊࡕࡢࡅࡕࡖ࡟ࡂࡗࡗࡓࡒࡇࡔࡆࠩร"): bstack111ll1ll1_opy_
      }
      if bstack1llllll11_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫฤ") in CONFIG:
        bstack11l111_opy_ = []
        manager = multiprocessing.Manager()
        bstack1l1ll1l11_opy_ = manager.list()
        if bstack111lll1l1_opy_(args):
          for index, platform in enumerate(CONFIG[bstack1llllll11_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬล")]):
            if index == 0:
              bstack1ll1l1l1_opy_[bstack1llllll11_opy_ (u"ࠪࡪ࡮ࡲࡥࡠࡰࡤࡱࡪ࠭ฦ")] = args
            bstack11l111_opy_.append(multiprocessing.Process(name=str(index),
                                          target=run_on_browserstack, args=(bstack1ll1l1l1_opy_, bstack1l1ll1l11_opy_)))
        else:
          for index, platform in enumerate(CONFIG[bstack1llllll11_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧว")]):
            bstack11l111_opy_.append(multiprocessing.Process(name=str(index),
                                          target=run_on_browserstack, args=(bstack1ll1l1l1_opy_, bstack1l1ll1l11_opy_)))
        for t in bstack11l111_opy_:
          t.start()
        for t in bstack11l111_opy_:
          t.join()
        bstack11l11l11l_opy_ = list(bstack1l1ll1l11_opy_)
      else:
        if bstack111lll1l1_opy_(args):
          bstack1ll1l1l1_opy_[bstack1llllll11_opy_ (u"ࠬ࡬ࡩ࡭ࡧࡢࡲࡦࡳࡥࠨศ")] = args
          test = multiprocessing.Process(name=str(0),
                                        target=run_on_browserstack, args=(bstack1ll1l1l1_opy_,))
          test.start()
          test.join()
        else:
          bstack11llll1ll_opy_(bstack11ll11l1_opy_)
          sys.path.append(os.path.dirname(os.path.abspath(args[0])))
          mod_globals = globals()
          mod_globals[bstack1llllll11_opy_ (u"࠭࡟ࡠࡰࡤࡱࡪࡥ࡟ࠨษ")] = bstack1llllll11_opy_ (u"ࠧࡠࡡࡰࡥ࡮ࡴ࡟ࡠࠩส")
          mod_globals[bstack1llllll11_opy_ (u"ࠨࡡࡢࡪ࡮ࡲࡥࡠࡡࠪห")] = os.path.abspath(args[0])
          sys.argv = sys.argv[2:]
          exec(open(args[0]).read(), mod_globals)
  elif bstack11ll1l1ll_opy_ == bstack1llllll11_opy_ (u"ࠩࡳࡥࡧࡵࡴࠨฬ") or bstack11ll1l1ll_opy_ == bstack1llllll11_opy_ (u"ࠪࡶࡴࡨ࡯ࡵࠩอ"):
    try:
      from pabot import pabot
    except Exception as e:
      bstack1ll1_opy_(e, bstack1ll1111ll_opy_)
    bstack1ll1l1ll_opy_()
    bstack11llll1ll_opy_(bstack111lll11_opy_)
    if bstack1llllll11_opy_ (u"ࠫ࠲࠳ࡰࡳࡱࡦࡩࡸࡹࡥࡴࠩฮ") in args:
      i = args.index(bstack1llllll11_opy_ (u"ࠬ࠳࠭ࡱࡴࡲࡧࡪࡹࡳࡦࡵࠪฯ"))
      args.pop(i)
      args.pop(i)
    args.insert(0, str(bstack1ll11l111_opy_))
    args.insert(0, str(bstack1llllll11_opy_ (u"࠭࠭࠮ࡲࡵࡳࡨ࡫ࡳࡴࡧࡶࠫะ")))
    pabot.main(args)
  elif bstack11ll1l1ll_opy_ == bstack1llllll11_opy_ (u"ࠧࡳࡱࡥࡳࡹ࠳ࡩ࡯ࡶࡨࡶࡳࡧ࡬ࠨั"):
    try:
      from robot import run_cli
    except Exception as e:
      bstack1ll1_opy_(e, bstack1ll1111ll_opy_)
    for a in args:
      if bstack1llllll11_opy_ (u"ࠨࡄࡖࡘࡆࡉࡋࡑࡎࡄࡘࡋࡕࡒࡎࡋࡑࡈࡊ࡞ࠧา") in a:
        bstack1111lll1l_opy_ = int(a.split(bstack1llllll11_opy_ (u"ࠩ࠽ࠫำ"))[1])
      if bstack1llllll11_opy_ (u"ࠪࡆࡘ࡚ࡁࡄࡍࡇࡉࡋࡒࡏࡄࡃࡏࡍࡉࡋࡎࡕࡋࡉࡍࡊࡘࠧิ") in a:
        bstack11111l11_opy_ = str(a.split(bstack1llllll11_opy_ (u"ࠫ࠿࠭ี"))[1])
      if bstack1llllll11_opy_ (u"ࠬࡈࡓࡕࡃࡆࡏࡈࡒࡉࡂࡔࡊࡗࠬึ") in a:
        bstack1l1l1l11l_opy_ = str(a.split(bstack1llllll11_opy_ (u"࠭࠺ࠨื"))[1])
    bstack1ll11l11l_opy_ = None
    if bstack1llllll11_opy_ (u"ࠧ࠮࠯ࡥࡷࡹࡧࡣ࡬ࡡ࡬ࡸࡪࡳ࡟ࡪࡰࡧࡩࡽุ࠭") in args:
      i = args.index(bstack1llllll11_opy_ (u"ࠨ࠯࠰ࡦࡸࡺࡡࡤ࡭ࡢ࡭ࡹ࡫࡭ࡠ࡫ࡱࡨࡪࡾูࠧ"))
      args.pop(i)
      bstack1ll11l11l_opy_ = args.pop(i)
    if bstack1ll11l11l_opy_ is not None:
      global bstack11l1l11_opy_
      bstack11l1l11_opy_ = bstack1ll11l11l_opy_
    bstack11llll1ll_opy_(bstack111lll11_opy_)
    run_cli(args)
  elif bstack11ll1l1ll_opy_ == bstack1llllll11_opy_ (u"ࠩࡳࡽࡹ࡫ࡳࡵฺࠩ"):
    try:
      from _pytest.config import _prepareconfig
      from _pytest.config import Config
      from _pytest import runner
      import importlib
      bstack1l1ll111l_opy_ = importlib.find_loader(bstack1llllll11_opy_ (u"ࠪࡴࡾࡺࡥࡴࡶࡢࡷࡪࡲࡥ࡯࡫ࡸࡱࠬ฻"))
    except Exception as e:
      logger.warn(e, bstack11ll1ll1l_opy_)
    bstack1ll1l1ll_opy_()
    try:
      if bstack1llllll11_opy_ (u"ࠫ࠲࠳ࡤࡳ࡫ࡹࡩࡷ࠭฼") in args:
        i = args.index(bstack1llllll11_opy_ (u"ࠬ࠳࠭ࡥࡴ࡬ࡺࡪࡸࠧ฽"))
        args.pop(i+1)
        args.pop(i)
      if bstack1llllll11_opy_ (u"࠭࠭࠮ࡲ࡯ࡹ࡬࡯࡮ࡴࠩ฾") in args:
        i = args.index(bstack1llllll11_opy_ (u"ࠧ࠮࠯ࡳࡰࡺ࡭ࡩ࡯ࡵࠪ฿"))
        args.pop(i+1)
        args.pop(i)
      if bstack1llllll11_opy_ (u"ࠨ࠯ࡳࠫเ") in args:
        i = args.index(bstack1llllll11_opy_ (u"ࠩ࠰ࡴࠬแ"))
        args.pop(i+1)
        args.pop(i)
      if bstack1llllll11_opy_ (u"ࠪ࠱࠲ࡴࡵ࡮ࡲࡵࡳࡨ࡫ࡳࡴࡧࡶࠫโ") in args:
        i = args.index(bstack1llllll11_opy_ (u"ࠫ࠲࠳࡮ࡶ࡯ࡳࡶࡴࡩࡥࡴࡵࡨࡷࠬใ"))
        args.pop(i+1)
        args.pop(i)
      if bstack1llllll11_opy_ (u"ࠬ࠳࡮ࠨไ") in args:
        i = args.index(bstack1llllll11_opy_ (u"࠭࠭࡯ࠩๅ"))
        args.pop(i+1)
        args.pop(i)
    except Exception as exc:
      logger.error(str(exc))
    config = _prepareconfig(args)
    bstack1l111l11_opy_ = config.args
    bstack1l1111l1l_opy_ = config.invocation_params.args
    bstack1l1111l1l_opy_ = list(bstack1l1111l1l_opy_)
    bstack11l1l111l_opy_ = [os.path.normpath(item) for item in bstack1l111l11_opy_]
    bstack1l1l1ll11_opy_ = [os.path.normpath(item) for item in bstack1l1111l1l_opy_]
    bstack11l1ll1l_opy_ = [item for item in bstack1l1l1ll11_opy_ if item not in bstack11l1l111l_opy_]
    if bstack1llllll11_opy_ (u"ࠧ࠮࠯ࡦࡥࡨ࡮ࡥ࠮ࡥ࡯ࡩࡦࡸࠧๆ") not in bstack11l1ll1l_opy_:
      bstack11l1ll1l_opy_.append(bstack1llllll11_opy_ (u"ࠨ࠯࠰ࡧࡦࡩࡨࡦ࠯ࡦࡰࡪࡧࡲࠨ็"))
    import platform as pf
    if pf.system().lower() == bstack1llllll11_opy_ (u"ࠩࡺ࡭ࡳࡪ࡯ࡸࡵ่ࠪ"):
      from pathlib import PureWindowsPath, PurePosixPath
      bstack1l111l11_opy_ = [str(PurePosixPath(PureWindowsPath(bstack11lll1_opy_)))
                    for bstack11lll1_opy_ in bstack1l111l11_opy_]
    if (bstack1llll1l11_opy_):
      bstack11l1ll1l_opy_.append(bstack1llllll11_opy_ (u"ࠪ࠱࠲ࡹ࡫ࡪࡲࡖࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫้ࠧ"))
      bstack11l1ll1l_opy_.append(bstack1llllll11_opy_ (u"࡙ࠫࡸࡵࡦ๊ࠩ"))
    try:
      from pytest_bdd import reporting
      bstack1ll1lll1l_opy_ = True
    except Exception as e:
      pass
    if (not bstack1ll1lll1l_opy_):
      bstack11l1ll1l_opy_.append(bstack1llllll11_opy_ (u"ࠬ࠳ࡰࠨ๋"))
      bstack11l1ll1l_opy_.append(bstack1llllll11_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹࡥࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡵࡲࡵࡨ࡫ࡱࠫ์"))
    bstack11l1ll1l_opy_.append(bstack1llllll11_opy_ (u"ࠧ࠮࠯ࡧࡶ࡮ࡼࡥࡳࠩํ"))
    bstack11l1ll1l_opy_.append(bstack1llllll11_opy_ (u"ࠨࡥ࡫ࡶࡴࡳࡥࠨ๎"))
    bstack1l11l1l1l_opy_ = []
    for spec in bstack1l111l11_opy_:
      bstack111l11_opy_ = []
      bstack111l11_opy_.append(spec)
      bstack111l11_opy_ += bstack11l1ll1l_opy_
      bstack1l11l1l1l_opy_.append(bstack111l11_opy_)
    bstack1l11l1111_opy_ = True
    bstack1ll1111l1_opy_ = 1
    if bstack1llllll11_opy_ (u"ࠩࡳࡥࡷࡧ࡬࡭ࡧ࡯ࡷࡕ࡫ࡲࡑ࡮ࡤࡸ࡫ࡵࡲ࡮ࠩ๏") in CONFIG:
      bstack1ll1111l1_opy_ = CONFIG[bstack1llllll11_opy_ (u"ࠪࡴࡦࡸࡡ࡭࡮ࡨࡰࡸࡖࡥࡳࡒ࡯ࡥࡹ࡬࡯ࡳ࡯ࠪ๐")]
    bstack1lll1ll1_opy_ = int(bstack1ll1111l1_opy_)*int(len(CONFIG[bstack1llllll11_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧ๑")]))
    execution_items = []
    for bstack111l11_opy_ in bstack1l11l1l1l_opy_:
      for index, _ in enumerate(CONFIG[bstack1llllll11_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨ๒")]):
        item = {}
        item[bstack1llllll11_opy_ (u"࠭ࡡࡳࡩࠪ๓")] = bstack111l11_opy_
        item[bstack1llllll11_opy_ (u"ࠧࡪࡰࡧࡩࡽ࠭๔")] = index
        execution_items.append(item)
    bstack111lll111_opy_ = bstack1ll1l11_opy_(execution_items, bstack1lll1ll1_opy_)
    for execution_item in bstack111lll111_opy_:
      bstack11l111_opy_ = []
      for item in execution_item:
        bstack11l111_opy_.append(bstack1l1lll111_opy_(name=str(item[bstack1llllll11_opy_ (u"ࠨ࡫ࡱࡨࡪࡾࠧ๕")]),
                                            target=bstack11l1111l_opy_,
                                            args=(item[bstack1llllll11_opy_ (u"ࠩࡤࡶ࡬࠭๖")],)))
      for t in bstack11l111_opy_:
        t.start()
      for t in bstack11l111_opy_:
        t.join()
  elif bstack11ll1l1ll_opy_ == bstack1llllll11_opy_ (u"ࠪࡦࡪ࡮ࡡࡷࡧࠪ๗"):
    try:
      from behave.__main__ import main as bstack11l1ll11l_opy_
      from behave.configuration import Configuration
    except Exception as e:
      bstack1ll1_opy_(e, bstack11ll111_opy_)
    bstack1ll1l1ll_opy_()
    bstack1l11l1111_opy_ = True
    bstack1ll1111l1_opy_ = 1
    if bstack1llllll11_opy_ (u"ࠫࡵࡧࡲࡢ࡮࡯ࡩࡱࡹࡐࡦࡴࡓࡰࡦࡺࡦࡰࡴࡰࠫ๘") in CONFIG:
      bstack1ll1111l1_opy_ = CONFIG[bstack1llllll11_opy_ (u"ࠬࡶࡡࡳࡣ࡯ࡰࡪࡲࡳࡑࡧࡵࡔࡱࡧࡴࡧࡱࡵࡱࠬ๙")]
    bstack1lll1ll1_opy_ = int(bstack1ll1111l1_opy_)*int(len(CONFIG[bstack1llllll11_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩ๚")]))
    config = Configuration(args)
    bstack1l1111l_opy_ = config.paths
    if len(bstack1l1111l_opy_) == 0:
      import glob
      pattern = bstack1llllll11_opy_ (u"ࠧࠫࠬ࠲࠮࠳࡬ࡥࡢࡶࡸࡶࡪ࠭๛")
      bstack11l1l1l1l_opy_ = glob.glob(pattern, recursive=True)
      args.extend(bstack11l1l1l1l_opy_)
      config = Configuration(args)
      bstack1l1111l_opy_ = config.paths
    bstack1l111l11_opy_ = [os.path.normpath(item) for item in bstack1l1111l_opy_]
    bstack1lll1ll11_opy_ = [os.path.normpath(item) for item in args]
    bstack1ll111l1_opy_ = [item for item in bstack1lll1ll11_opy_ if item not in bstack1l111l11_opy_]
    import platform as pf
    if pf.system().lower() == bstack1llllll11_opy_ (u"ࠨࡹ࡬ࡲࡩࡵࡷࡴࠩ๜"):
      from pathlib import PureWindowsPath, PurePosixPath
      bstack1l111l11_opy_ = [str(PurePosixPath(PureWindowsPath(bstack11lll1_opy_)))
                    for bstack11lll1_opy_ in bstack1l111l11_opy_]
    bstack1l11l1l1l_opy_ = []
    for spec in bstack1l111l11_opy_:
      bstack111l11_opy_ = []
      bstack111l11_opy_ += bstack1ll111l1_opy_
      bstack111l11_opy_.append(spec)
      bstack1l11l1l1l_opy_.append(bstack111l11_opy_)
    execution_items = []
    for bstack111l11_opy_ in bstack1l11l1l1l_opy_:
      for index, _ in enumerate(CONFIG[bstack1llllll11_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬ๝")]):
        item = {}
        item[bstack1llllll11_opy_ (u"ࠪࡥࡷ࡭ࠧ๞")] = bstack1llllll11_opy_ (u"ࠫࠥ࠭๟").join(bstack111l11_opy_)
        item[bstack1llllll11_opy_ (u"ࠬ࡯࡮ࡥࡧࡻࠫ๠")] = index
        execution_items.append(item)
    bstack111lll111_opy_ = bstack1ll1l11_opy_(execution_items, bstack1lll1ll1_opy_)
    for execution_item in bstack111lll111_opy_:
      bstack11l111_opy_ = []
      for item in execution_item:
        bstack11l111_opy_.append(bstack1l1lll111_opy_(name=str(item[bstack1llllll11_opy_ (u"࠭ࡩ࡯ࡦࡨࡼࠬ๡")]),
                                            target=bstack1111_opy_,
                                            args=(item[bstack1llllll11_opy_ (u"ࠧࡢࡴࡪࠫ๢")],)))
      for t in bstack11l111_opy_:
        t.start()
      for t in bstack11l111_opy_:
        t.join()
  else:
    bstack1l1lll1_opy_(bstack1lllll1ll_opy_)
  if not bstack1l111l1ll_opy_:
    bstack1ll1l1lll_opy_()
def browserstack_initialize(bstack111l11l1l_opy_=None):
  run_on_browserstack(bstack111l11l1l_opy_, None, True)
def bstack1ll1l1lll_opy_():
  [bstack1111lll_opy_, bstack11ll11l11_opy_] = bstack1ll1l11l1_opy_()
  if bstack1111lll_opy_ is not None and bstack1l1lll1l_opy_() != -1:
    sessions = bstack11l1111_opy_(bstack1111lll_opy_)
    bstack11l1ll1ll_opy_(sessions, bstack11ll11l11_opy_)
def bstack11ll1ll1_opy_(bstack1l111l1l1_opy_):
    if bstack1l111l1l1_opy_:
        return bstack1l111l1l1_opy_.capitalize()
    else:
        return bstack1l111l1l1_opy_
def bstack111111_opy_(bstack111l111_opy_):
    if bstack1llllll11_opy_ (u"ࠨࡰࡤࡱࡪ࠭๣") in bstack111l111_opy_ and bstack111l111_opy_[bstack1llllll11_opy_ (u"ࠩࡱࡥࡲ࡫ࠧ๤")] != bstack1llllll11_opy_ (u"ࠪࠫ๥"):
        return bstack111l111_opy_[bstack1llllll11_opy_ (u"ࠫࡳࡧ࡭ࡦࠩ๦")]
    else:
        bstack1l1_opy_ = bstack1llllll11_opy_ (u"ࠧࠨ๧")
        if bstack1llllll11_opy_ (u"࠭ࡤࡦࡸ࡬ࡧࡪ࠭๨") in bstack111l111_opy_ and bstack111l111_opy_[bstack1llllll11_opy_ (u"ࠧࡥࡧࡹ࡭ࡨ࡫ࠧ๩")] != None:
            bstack1l1_opy_ += bstack111l111_opy_[bstack1llllll11_opy_ (u"ࠨࡦࡨࡺ࡮ࡩࡥࠨ๪")] + bstack1llllll11_opy_ (u"ࠤ࠯ࠤࠧ๫")
            if bstack111l111_opy_[bstack1llllll11_opy_ (u"ࠪࡳࡸ࠭๬")] == bstack1llllll11_opy_ (u"ࠦ࡮ࡵࡳࠣ๭"):
                bstack1l1_opy_ += bstack1llllll11_opy_ (u"ࠧ࡯ࡏࡔࠢࠥ๮")
            bstack1l1_opy_ += (bstack111l111_opy_[bstack1llllll11_opy_ (u"࠭࡯ࡴࡡࡹࡩࡷࡹࡩࡰࡰࠪ๯")] or bstack1llllll11_opy_ (u"ࠧࠨ๰"))
            return bstack1l1_opy_
        else:
            bstack1l1_opy_ += bstack11ll1ll1_opy_(bstack111l111_opy_[bstack1llllll11_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࠩ๱")]) + bstack1llllll11_opy_ (u"ࠤࠣࠦ๲") + (bstack111l111_opy_[bstack1llllll11_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬ๳")] or bstack1llllll11_opy_ (u"ࠫࠬ๴")) + bstack1llllll11_opy_ (u"ࠧ࠲ࠠࠣ๵")
            if bstack111l111_opy_[bstack1llllll11_opy_ (u"࠭࡯ࡴࠩ๶")] == bstack1llllll11_opy_ (u"ࠢࡘ࡫ࡱࡨࡴࡽࡳࠣ๷"):
                bstack1l1_opy_ += bstack1llllll11_opy_ (u"࡙ࠣ࡬ࡲࠥࠨ๸")
            bstack1l1_opy_ += bstack111l111_opy_[bstack1llllll11_opy_ (u"ࠩࡲࡷࡤࡼࡥࡳࡵ࡬ࡳࡳ࠭๹")] or bstack1llllll11_opy_ (u"ࠪࠫ๺")
            return bstack1l1_opy_
def bstack1ll1l1ll1_opy_(bstack11l1lllll_opy_):
    if bstack11l1lllll_opy_ == bstack1llllll11_opy_ (u"ࠦࡩࡵ࡮ࡦࠤ๻"):
        return bstack1llllll11_opy_ (u"ࠬࡂࡴࡥࠢࡦࡰࡦࡹࡳ࠾ࠤࡥࡷࡹࡧࡣ࡬࠯ࡧࡥࡹࡧࠢࠡࡵࡷࡽࡱ࡫࠽ࠣࡥࡲࡰࡴࡸ࠺ࡨࡴࡨࡩࡳࡁࠢ࠿࠾ࡩࡳࡳࡺࠠࡤࡱ࡯ࡳࡷࡃࠢࡨࡴࡨࡩࡳࠨ࠾ࡄࡱࡰࡴࡱ࡫ࡴࡦࡦ࠿࠳࡫ࡵ࡮ࡵࡀ࠿࠳ࡹࡪ࠾ࠨ๼")
    elif bstack11l1lllll_opy_ == bstack1llllll11_opy_ (u"ࠨࡦࡢ࡫࡯ࡩࡩࠨ๽"):
        return bstack1llllll11_opy_ (u"ࠧ࠽ࡶࡧࠤࡨࡲࡡࡴࡵࡀࠦࡧࡹࡴࡢࡥ࡮࠱ࡩࡧࡴࡢࠤࠣࡷࡹࡿ࡬ࡦ࠿ࠥࡧࡴࡲ࡯ࡳ࠼ࡵࡩࡩࡁࠢ࠿࠾ࡩࡳࡳࡺࠠࡤࡱ࡯ࡳࡷࡃࠢࡳࡧࡧࠦࡃࡌࡡࡪ࡮ࡨࡨࡁ࠵ࡦࡰࡰࡷࡂࡁ࠵ࡴࡥࡀࠪ๾")
    elif bstack11l1lllll_opy_ == bstack1llllll11_opy_ (u"ࠣࡲࡤࡷࡸ࡫ࡤࠣ๿"):
        return bstack1llllll11_opy_ (u"ࠩ࠿ࡸࡩࠦࡣ࡭ࡣࡶࡷࡂࠨࡢࡴࡶࡤࡧࡰ࠳ࡤࡢࡶࡤࠦࠥࡹࡴࡺ࡮ࡨࡁࠧࡩ࡯࡭ࡱࡵ࠾࡬ࡸࡥࡦࡰ࠾ࠦࡃࡂࡦࡰࡰࡷࠤࡨࡵ࡬ࡰࡴࡀࠦ࡬ࡸࡥࡦࡰࠥࡂࡕࡧࡳࡴࡧࡧࡀ࠴࡬࡯࡯ࡶࡁࡀ࠴ࡺࡤ࠿ࠩ຀")
    elif bstack11l1lllll_opy_ == bstack1llllll11_opy_ (u"ࠥࡩࡷࡸ࡯ࡳࠤກ"):
        return bstack1llllll11_opy_ (u"ࠫࡁࡺࡤࠡࡥ࡯ࡥࡸࡹ࠽ࠣࡤࡶࡸࡦࡩ࡫࠮ࡦࡤࡸࡦࠨࠠࡴࡶࡼࡰࡪࡃࠢࡤࡱ࡯ࡳࡷࡀࡲࡦࡦ࠾ࠦࡃࡂࡦࡰࡰࡷࠤࡨࡵ࡬ࡰࡴࡀࠦࡷ࡫ࡤࠣࡀࡈࡶࡷࡵࡲ࠽࠱ࡩࡳࡳࡺ࠾࠽࠱ࡷࡨࡃ࠭ຂ")
    elif bstack11l1lllll_opy_ == bstack1llllll11_opy_ (u"ࠧࡺࡩ࡮ࡧࡲࡹࡹࠨ຃"):
        return bstack1llllll11_opy_ (u"࠭࠼ࡵࡦࠣࡧࡱࡧࡳࡴ࠿ࠥࡦࡸࡺࡡࡤ࡭࠰ࡨࡦࡺࡡࠣࠢࡶࡸࡾࡲࡥ࠾ࠤࡦࡳࡱࡵࡲ࠻ࠥࡨࡩࡦ࠹࠲࠷࠽ࠥࡂࡁ࡬࡯࡯ࡶࠣࡧࡴࡲ࡯ࡳ࠿ࠥࠧࡪ࡫ࡡ࠴࠴࠹ࠦࡃ࡚ࡩ࡮ࡧࡲࡹࡹࡂ࠯ࡧࡱࡱࡸࡃࡂ࠯ࡵࡦࡁࠫຄ")
    elif bstack11l1lllll_opy_ == bstack1llllll11_opy_ (u"ࠢࡳࡷࡱࡲ࡮ࡴࡧࠣ຅"):
        return bstack1llllll11_opy_ (u"ࠨ࠾ࡷࡨࠥࡩ࡬ࡢࡵࡶࡁࠧࡨࡳࡵࡣࡦ࡯࠲ࡪࡡࡵࡣࠥࠤࡸࡺࡹ࡭ࡧࡀࠦࡨࡵ࡬ࡰࡴ࠽ࡦࡱࡧࡣ࡬࠽ࠥࡂࡁ࡬࡯࡯ࡶࠣࡧࡴࡲ࡯ࡳ࠿ࠥࡦࡱࡧࡣ࡬ࠤࡁࡖࡺࡴ࡮ࡪࡰࡪࡀ࠴࡬࡯࡯ࡶࡁࡀ࠴ࡺࡤ࠿ࠩຆ")
    else:
        return bstack1llllll11_opy_ (u"ࠩ࠿ࡸࡩࠦࡡ࡭࡫ࡪࡲࡂࠨࡣࡦࡰࡷࡩࡷࠨࠠࡤ࡮ࡤࡷࡸࡃࠢࡣࡵࡷࡥࡨࡱ࠭ࡥࡣࡷࡥࠧࠦࡳࡵࡻ࡯ࡩࡂࠨࡣࡰ࡮ࡲࡶ࠿ࡨ࡬ࡢࡥ࡮࠿ࠧࡄ࠼ࡧࡱࡱࡸࠥࡩ࡯࡭ࡱࡵࡁࠧࡨ࡬ࡢࡥ࡮ࠦࡃ࠭ງ")+bstack11ll1ll1_opy_(bstack11l1lllll_opy_)+bstack1llllll11_opy_ (u"ࠪࡀ࠴࡬࡯࡯ࡶࡁࡀ࠴ࡺࡤ࠿ࠩຈ")
def bstack1lll111ll_opy_(session):
    return bstack1llllll11_opy_ (u"ࠫࡁࡺࡲࠡࡥ࡯ࡥࡸࡹ࠽ࠣࡤࡶࡸࡦࡩ࡫࠮ࡴࡲࡻࠧࡄ࠼ࡵࡦࠣࡧࡱࡧࡳࡴ࠿ࠥࡦࡸࡺࡡࡤ࡭࠰ࡨࡦࡺࡡࠡࡵࡨࡷࡸ࡯࡯࡯࠯ࡱࡥࡲ࡫ࠢ࠿࠾ࡤࠤ࡭ࡸࡥࡧ࠿ࠥࡿࢂࠨࠠࡵࡣࡵ࡫ࡪࡺ࠽ࠣࡡࡥࡰࡦࡴ࡫ࠣࡀࡾࢁࡁ࠵ࡡ࠿࠾࠲ࡸࡩࡄࡻࡾࡽࢀࡀࡹࡪࠠࡢ࡮࡬࡫ࡳࡃࠢࡤࡧࡱࡸࡪࡸࠢࠡࡥ࡯ࡥࡸࡹ࠽ࠣࡤࡶࡸࡦࡩ࡫࠮ࡦࡤࡸࡦࠨ࠾ࡼࡿ࠿࠳ࡹࡪ࠾࠽ࡶࡧࠤࡦࡲࡩࡨࡰࡀࠦࡨ࡫࡮ࡵࡧࡵࠦࠥࡩ࡬ࡢࡵࡶࡁࠧࡨࡳࡵࡣࡦ࡯࠲ࡪࡡࡵࡣࠥࡂࢀࢃ࠼࠰ࡶࡧࡂࡁࡺࡤࠡࡣ࡯࡭࡬ࡴ࠽ࠣࡥࡨࡲࡹ࡫ࡲࠣࠢࡦࡰࡦࡹࡳ࠾ࠤࡥࡷࡹࡧࡣ࡬࠯ࡧࡥࡹࡧࠢ࠿ࡽࢀࡀ࠴ࡺࡤ࠿࠾ࡷࡨࠥࡧ࡬ࡪࡩࡱࡁࠧࡩࡥ࡯ࡶࡨࡶࠧࠦࡣ࡭ࡣࡶࡷࡂࠨࡢࡴࡶࡤࡧࡰ࠳ࡤࡢࡶࡤࠦࡃࢁࡽ࠽࠱ࡷࡨࡃࡂ࠯ࡵࡴࡁࠫຉ").format(session[bstack1llllll11_opy_ (u"ࠬࡶࡵࡣ࡮࡬ࡧࡤࡻࡲ࡭ࠩຊ")],bstack111111_opy_(session), bstack1ll1l1ll1_opy_(session[bstack1llllll11_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤࡹࡴࡢࡶࡸࡷࠬ຋")]), bstack1ll1l1ll1_opy_(session[bstack1llllll11_opy_ (u"ࠧࡴࡶࡤࡸࡺࡹࠧຌ")]), bstack11ll1ll1_opy_(session[bstack1llllll11_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࠩຍ")] or session[bstack1llllll11_opy_ (u"ࠩࡧࡩࡻ࡯ࡣࡦࠩຎ")] or bstack1llllll11_opy_ (u"ࠪࠫຏ")) + bstack1llllll11_opy_ (u"ࠦࠥࠨຐ") + (session[bstack1llllll11_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡥࡶࡦࡴࡶ࡭ࡴࡴࠧຑ")] or bstack1llllll11_opy_ (u"࠭ࠧຒ")), session[bstack1llllll11_opy_ (u"ࠧࡰࡵࠪຓ")] + bstack1llllll11_opy_ (u"ࠣࠢࠥດ") + session[bstack1llllll11_opy_ (u"ࠩࡲࡷࡤࡼࡥࡳࡵ࡬ࡳࡳ࠭ຕ")], session[bstack1llllll11_opy_ (u"ࠪࡨࡺࡸࡡࡵ࡫ࡲࡲࠬຖ")] or bstack1llllll11_opy_ (u"ࠫࠬທ"), session[bstack1llllll11_opy_ (u"ࠬࡩࡲࡦࡣࡷࡩࡩࡥࡡࡵࠩຘ")] if session[bstack1llllll11_opy_ (u"࠭ࡣࡳࡧࡤࡸࡪࡪ࡟ࡢࡶࠪນ")] else bstack1llllll11_opy_ (u"ࠧࠨບ"))
def bstack11l1ll1ll_opy_(sessions, bstack11ll11l11_opy_):
  try:
    bstack1l111lll1_opy_ = bstack1llllll11_opy_ (u"ࠣࠤປ")
    if not os.path.exists(bstack1l111l_opy_):
      os.mkdir(bstack1l111l_opy_)
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), bstack1llllll11_opy_ (u"ࠩࡤࡷࡸ࡫ࡴࡴ࠱ࡵࡩࡵࡵࡲࡵ࠰࡫ࡸࡲࡲࠧຜ")), bstack1llllll11_opy_ (u"ࠪࡶࠬຝ")) as f:
      bstack1l111lll1_opy_ = f.read()
    bstack1l111lll1_opy_ = bstack1l111lll1_opy_.replace(bstack1llllll11_opy_ (u"ࠫࢀࠫࡒࡆࡕࡘࡐ࡙࡙࡟ࡄࡑࡘࡒ࡙ࠫࡽࠨພ"), str(len(sessions)))
    bstack1l111lll1_opy_ = bstack1l111lll1_opy_.replace(bstack1llllll11_opy_ (u"ࠬࢁࠥࡃࡗࡌࡐࡉࡥࡕࡓࡎࠨࢁࠬຟ"), bstack11ll11l11_opy_)
    bstack1l111lll1_opy_ = bstack1l111lll1_opy_.replace(bstack1llllll11_opy_ (u"࠭ࡻࠦࡄࡘࡍࡑࡊ࡟ࡏࡃࡐࡉࠪࢃࠧຠ"), sessions[0].get(bstack1llllll11_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡥ࡮ࡢ࡯ࡨࠫມ")) if sessions[0] else bstack1llllll11_opy_ (u"ࠨࠩຢ"))
    with open(os.path.join(bstack1l111l_opy_, bstack1llllll11_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠮ࡴࡨࡴࡴࡸࡴ࠯ࡪࡷࡱࡱ࠭ຣ")), bstack1llllll11_opy_ (u"ࠪࡻࠬ຤")) as stream:
      stream.write(bstack1l111lll1_opy_.split(bstack1llllll11_opy_ (u"ࠫࢀࠫࡓࡆࡕࡖࡍࡔࡔࡓࡠࡆࡄࡘࡆࠫࡽࠨລ"))[0])
      for session in sessions:
        stream.write(bstack1lll111ll_opy_(session))
      stream.write(bstack1l111lll1_opy_.split(bstack1llllll11_opy_ (u"ࠬࢁࠥࡔࡇࡖࡗࡎࡕࡎࡔࡡࡇࡅ࡙ࡇࠥࡾࠩ຦"))[1])
    logger.info(bstack1llllll11_opy_ (u"࠭ࡇࡦࡰࡨࡶࡦࡺࡥࡥࠢࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠡࡤࡸ࡭ࡱࡪࠠࡢࡴࡷ࡭࡫ࡧࡣࡵࡵࠣࡥࡹࠦࡻࡾࠩວ").format(bstack1l111l_opy_));
  except Exception as e:
    logger.debug(bstack1l11llll_opy_.format(str(e)))
def bstack11l1111_opy_(bstack1111lll_opy_):
  global CONFIG
  try:
    host = bstack1llllll11_opy_ (u"ࠧࡢࡲ࡬࠱ࡨࡲ࡯ࡶࡦࠪຨ") if bstack1llllll11_opy_ (u"ࠨࡣࡳࡴࠬຩ") in CONFIG else bstack1llllll11_opy_ (u"ࠩࡤࡴ࡮࠭ສ")
    user = CONFIG[bstack1llllll11_opy_ (u"ࠪࡹࡸ࡫ࡲࡏࡣࡰࡩࠬຫ")]
    key = CONFIG[bstack1llllll11_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶࡏࡪࡿࠧຬ")]
    bstack1ll1lll11_opy_ = bstack1llllll11_opy_ (u"ࠬࡧࡰࡱ࠯ࡤࡹࡹࡵ࡭ࡢࡶࡨࠫອ") if bstack1llllll11_opy_ (u"࠭ࡡࡱࡲࠪຮ") in CONFIG else bstack1llllll11_opy_ (u"ࠧࡢࡷࡷࡳࡲࡧࡴࡦࠩຯ")
    url = bstack1llllll11_opy_ (u"ࠨࡪࡷࡸࡵࡹ࠺࠰࠱ࡾࢁ࠿ࢁࡽࡁࡽࢀ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡧࡴࡳ࠯ࡼࡿ࠲ࡦࡺ࡯࡬ࡥࡵ࠲ࡿࢂ࠵ࡳࡦࡵࡶ࡭ࡴࡴࡳ࠯࡬ࡶࡳࡳ࠭ະ").format(user, key, host, bstack1ll1lll11_opy_, bstack1111lll_opy_)
    headers = {
      bstack1llllll11_opy_ (u"ࠩࡆࡳࡳࡺࡥ࡯ࡶ࠰ࡸࡾࡶࡥࠨັ"): bstack1llllll11_opy_ (u"ࠪࡥࡵࡶ࡬ࡪࡥࡤࡸ࡮ࡵ࡮࠰࡬ࡶࡳࡳ࠭າ"),
    }
    proxies = bstack1lll1l1l1_opy_(CONFIG, url)
    response = requests.get(url, headers=headers, proxies=proxies)
    if response.json():
      return list(map(lambda session: session[bstack1llllll11_opy_ (u"ࠫࡦࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࡠࡵࡨࡷࡸ࡯࡯࡯ࠩຳ")], response.json()))
  except Exception as e:
    logger.debug(bstack1l11ll1l1_opy_.format(str(e)))
def bstack1ll1l11l1_opy_():
  global CONFIG
  try:
    if bstack1llllll11_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡒࡦࡳࡥࠨິ") in CONFIG:
      host = bstack1llllll11_opy_ (u"࠭ࡡࡱ࡫࠰ࡧࡱࡵࡵࡥࠩີ") if bstack1llllll11_opy_ (u"ࠧࡢࡲࡳࠫຶ") in CONFIG else bstack1llllll11_opy_ (u"ࠨࡣࡳ࡭ࠬື")
      user = CONFIG[bstack1llllll11_opy_ (u"ࠩࡸࡷࡪࡸࡎࡢ࡯ࡨຸࠫ")]
      key = CONFIG[bstack1llllll11_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵࡎࡩࡾູ࠭")]
      bstack1ll1lll11_opy_ = bstack1llllll11_opy_ (u"ࠫࡦࡶࡰ࠮ࡣࡸࡸࡴࡳࡡࡵࡧ຺ࠪ") if bstack1llllll11_opy_ (u"ࠬࡧࡰࡱࠩົ") in CONFIG else bstack1llllll11_opy_ (u"࠭ࡡࡶࡶࡲࡱࡦࡺࡥࠨຼ")
      url = bstack1llllll11_opy_ (u"ࠧࡩࡶࡷࡴࡸࡀ࠯࠰ࡽࢀ࠾ࢀࢃࡀࡼࡿ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡦࡳࡲ࠵ࡻࡾ࠱ࡥࡹ࡮ࡲࡤࡴ࠰࡭ࡷࡴࡴࠧຽ").format(user, key, host, bstack1ll1lll11_opy_)
      headers = {
        bstack1llllll11_opy_ (u"ࠨࡅࡲࡲࡹ࡫࡮ࡵ࠯ࡷࡽࡵ࡫ࠧ຾"): bstack1llllll11_opy_ (u"ࠩࡤࡴࡵࡲࡩࡤࡣࡷ࡭ࡴࡴ࠯࡫ࡵࡲࡲࠬ຿"),
      }
      if bstack1llllll11_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬເ") in CONFIG:
        params = {bstack1llllll11_opy_ (u"ࠫࡳࡧ࡭ࡦࠩແ"):CONFIG[bstack1llllll11_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡒࡦࡳࡥࠨໂ")], bstack1llllll11_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡤ࡯ࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩໃ"):CONFIG[bstack1llllll11_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩໄ")]}
      else:
        params = {bstack1llllll11_opy_ (u"ࠨࡰࡤࡱࡪ࠭໅"):CONFIG[bstack1llllll11_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡏࡣࡰࡩࠬໆ")]}
      proxies = bstack1lll1l1l1_opy_(CONFIG, url)
      response = requests.get(url, params=params, headers=headers, proxies=proxies)
      if response.json():
        bstack1l11111l_opy_ = response.json()[0][bstack1llllll11_opy_ (u"ࠪࡥࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴ࡟ࡣࡷ࡬ࡰࡩ࠭໇")]
        if bstack1l11111l_opy_:
          bstack11ll11l11_opy_ = bstack1l11111l_opy_[bstack1llllll11_opy_ (u"ࠫࡵࡻࡢ࡭࡫ࡦࡣࡺࡸ࡬ࠨ່")].split(bstack1llllll11_opy_ (u"ࠬࡶࡵࡣ࡮࡬ࡧ࠲ࡨࡵࡪ࡮ࡧ້ࠫ"))[0] + bstack1llllll11_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡸ࠵໊ࠧ") + bstack1l11111l_opy_[bstack1llllll11_opy_ (u"ࠧࡩࡣࡶ࡬ࡪࡪ࡟ࡪࡦ໋ࠪ")]
          logger.info(bstack1l1ll1l1_opy_.format(bstack11ll11l11_opy_))
          bstack1l1111l1_opy_ = CONFIG[bstack1llllll11_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫ໌")]
          if bstack1llllll11_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫໍ") in CONFIG:
            bstack1l1111l1_opy_ += bstack1llllll11_opy_ (u"ࠪࠤࠬ໎") + CONFIG[bstack1llllll11_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭໏")]
          if bstack1l1111l1_opy_!= bstack1l11111l_opy_[bstack1llllll11_opy_ (u"ࠬࡴࡡ࡮ࡧࠪ໐")]:
            logger.debug(bstack1ll1l111_opy_.format(bstack1l11111l_opy_[bstack1llllll11_opy_ (u"࠭࡮ࡢ࡯ࡨࠫ໑")], bstack1l1111l1_opy_))
          return [bstack1l11111l_opy_[bstack1llllll11_opy_ (u"ࠧࡩࡣࡶ࡬ࡪࡪ࡟ࡪࡦࠪ໒")], bstack11ll11l11_opy_]
    else:
      logger.warn(bstack1l11l11ll_opy_)
  except Exception as e:
    logger.debug(bstack1l1111_opy_.format(str(e)))
  return [None, None]
def bstack11l1l1lll_opy_(url, bstack11l11l_opy_=False):
  global CONFIG
  global bstack11ll11l_opy_
  if not bstack11ll11l_opy_:
    hostname = bstack1l1l1lll1_opy_(url)
    is_private = bstack1l11111_opy_(hostname)
    if (bstack1llllll11_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡌࡰࡥࡤࡰࠬ໓") in CONFIG and not CONFIG[bstack1llllll11_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡍࡱࡦࡥࡱ࠭໔")]) and (is_private or bstack11l11l_opy_):
      bstack11ll11l_opy_ = hostname
def bstack1l1l1lll1_opy_(url):
  return urlparse(url).hostname
def bstack1l11111_opy_(hostname):
  for bstack1ll1lll_opy_ in bstack1lllll_opy_:
    regex = re.compile(bstack1ll1lll_opy_)
    if regex.match(hostname):
      return True
  return False