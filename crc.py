
class CRC_CCITT:
   def __init__(self):
      self.tab=256*[[]]
      for i in xrange(256):
         crc=0
         c = i << 8

         for j in xrange(8):
            if (crc ^ c) & 0x8000:
               crc = ( crc << 1) ^ 0x1021
            else:
                  crc = crc << 1

            c = c << 1

            crc = crc & 0xffff

         self.tab[i]=crc
   
   def update_crc(self, crc, c):
      short_c=0x00ff & (c % 256)

      tmp = ((crc >> 8) ^ short_c) & 0xffff
      crc = (((crc << 8) ^ self.tab[tmp])) & 0xffff

      return crc
      
      
   def convertToAsccii(self,s):
      tempstr=""
      i=0
      while i+1 < len(s):
         tempstr+=   chr(int(   str(s[i])+str(s[i+1]),16))
         i+=2
      return tempstr;
    
   def calculate_crc_from_hex(self,s):
      tempstr=self.convertToAsccii(s)
      crcval=0xffff
      for c in tempstr:
         crcval=self.update_crc(crcval, ord(c))
      return '%04x' %crcval;      
      

test=CRC_CCITT()
print 'original: '+'$1012DA045BF7D6'
UsedStr='12DA04'
print'ok: '+str(test.calculate_crc_from_hex(UsedStr)) + ' used: ' +UsedStr

print 'original: '+'$1017DA04B007B6'

UsedStr='17DA04'
print'ok: '+str(test.calculate_crc_from_hex(UsedStr)) + ' used: ' +UsedStr

print 'original: '+'$1E16DA04000000000000FF4B80FE'
UsedStr='16DA04000000000000FF'
print'ok: '+str(test.calculate_crc_from_hex(UsedStr)) + ' used: ' +UsedStr


print 'original: '+'$1E15DA04FF0000000000FF5F3E01'
UsedStr='15DA04FF0000000000FF'
print'ok: '+str(test.calculate_crc_from_hex(UsedStr)) + ' used: ' +UsedStr

exit()
 
 
 