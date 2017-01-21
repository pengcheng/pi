class PTReceiver:
  def __init__(self):
    pass

  def onReceive(data, rawdata):
    pass


class PTMsg:
  def __init__(self):
    self.data = []
    self.data_size = 100
    self.current_position = 0
    for i in xrange(0, self.data_size):
      self.data.append(0)
    self.PREFIX0 = 0x42
    self.PREFIX1 = 0x4d

    self.receiver = None

  def setReceiver(self, receiver):
    self.receiver = receiver

  def setSize(self, size):
    if size > self.data_size:
      for i in xrange(0, size - self.data_size):
        self.data.append(0)
    self.data_size = size

  def feedOne(self, data):
    if self.current_position >= self.data_size:
      self.current_position = 0

    data = ord(data)
    if self.current_position == 0:
      if data != self.PREFIX0: return
    elif self.current_position == 1:
      if data != self.PREFIX1:
        self.current_position = 0
        return
    elif self.current_position == 3:
      size = self.data[2] * 256 + data
      if size < 10 or size > 256:
        self.current_position = 0
        return
      self.setSize(size + 4)

    self.data[self.current_position] = data
    self.current_position += 1

  def decode40(self):
    ret = {}
    ret['frame_length'] = self.data[2] * 256 +  self.data[3]
    ret['pm1p0_cf1']        = self.data[4] * 256 +  self.data[5]
    ret['pm2p5_cf1']        = self.data[6] * 256 +  self.data[7]
    ret['pm10p0_cf1']         = self.data[8] * 256 +  self.data[9]
    ret['pm1p0_air']    = self.data[10] * 256 + self.data[11]
    ret['pm2p5_air']    = self.data[12] * 256 + self.data[13]
    ret['pm10p0_air']     = self.data[14] * 256 + self.data[15]
    ret['cnt_0p3']      = self.data[16] * 256 + self.data[17]
    ret['cnt_0p5']      = self.data[18] * 256 + self.data[19]
    ret['cnt_1p0']      = self.data[20] * 256 + self.data[21]
    ret['cnt_2p5']      = self.data[22] * 256 + self.data[23]
    ret['cnt_5p0']      = self.data[24] * 256 + self.data[25]
    ret['cnt_10p0']      = self.data[26] * 256 + self.data[27]
    ret['formaldehyde'] = self.data[28] * 256 + self.data[29]
    ret['temperature']  = self.data[30] * 256 + self.data[31]
    ret['humidity']     = self.data[32] * 256 + self.data[33]
    # 34/35 not used
    ret['version']      = self.data[36]
    ret['error']        = self.data[37]
    ret['check']        = self.data[38] * 256 + self.data[39]
    ret['check_data']   = self.check()
    return ret

  def decode32(self):
    ret = {}
    ret['frame_length'] = self.data[2] * 256 +  self.data[3]
    ret['pm1p0_cf1']        = self.data[4] * 256 +  self.data[5]
    ret['pm2p5_cf1']        = self.data[6] * 256 +  self.data[7]
    ret['pm10p0_cf1']         = self.data[8] * 256 +  self.data[9]
    ret['pm1p0_air']    = self.data[10] * 256 + self.data[11]
    ret['pm2p5_air']    = self.data[12] * 256 + self.data[13]
    ret['pm10p0_air']     = self.data[14] * 256 + self.data[15]
    ret['cnt_0p3']      = self.data[16] * 256 + self.data[17]
    ret['cnt_0p5']      = self.data[18] * 256 + self.data[19]
    ret['cnt_1p0']      = self.data[20] * 256 + self.data[21]
    ret['cnt_2p5']      = self.data[22] * 256 + self.data[23]
    ret['cnt_5p0']      = self.data[24] * 256 + self.data[25]
    ret['cnt_10p0']      = self.data[26] * 256 + self.data[27]
    ret['version']      = self.data[28]
    ret['error']        = self.data[29]
    ret['check']        = self.data[30] * 256 + self.data[31]
    ret['check_data']   = self.check()
    return ret

  def decode(self):
    if self.data_size == 40:
      return self.decode40()
    if self.data_size == 32:
      return self.decode32()
    return {}

  def check(self):
    code = 0
    for i in range(0, self.data_size - 2):
      code += self.data[i]
    return code

  def rawdata(self):
    ret = ''
    for i in range(0, self.data_size):
      ret += '%02X' % self.data[i]
    return ret

  def p(self):
    ret = ''
    for i in self.data:
      ret += '%02X,' % i
    print ret
    print self.decode()

  def feed(self, data):
    for i in data:
      self.feedOne(i)
      if self.current_position >= self.data_size:
        if self.receiver:
          self.receiver.onReceive(self.decode(), self.rawdata())
        else:
          self.p()