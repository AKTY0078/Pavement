import math
import numpy as np

class AASHTOPavementDesign1993:
    def __init__(self):
        """
        คลาสสำหรับการออกแบบถนนลาดยางตาม AASHTO 1993
        """
        self.reliability_factors = {
            50: 0.000,
            60: -0.253,
            70: -0.524,
            75: -0.674,
            80: -0.841,
            85: -1.037,
            90: -1.282,
            95: -1.645,
            99: -2.326,
            99.9: -3.090
        }
    
    def calculate_structural_number(self, w18, reliability=90, overall_standard_deviation=0.44,
                                  initial_psi=4.2, terminal_psi=2.5, subgrade_mr=5000):
        """
        คำนวณ Structural Number (SN) ตาม AASHTO 1993
        
        Parameters:
        - w18: จำนวน 18-kip ESAL ในช่วงออกแบบ
        - reliability: ความเชื่อถือได้ (%)
        - overall_standard_deviation: ค่าเบี่ยงเบนมาตรฐานโดยรวม
        - initial_psi: PSI เริ่มต้น
        - terminal_psi: PSI สุดท้าย
        - subgrade_mr: Modulus of Resilience ของดินเดิม (psi)
        
        Returns:
        - structural_number: ค่า SN ที่คำนวณได้
        """
        
        # ค่า Zr จากระดับความเชื่อถือได้
        if reliability in self.reliability_factors:
            zr = self.reliability_factors[reliability]
        else:
            # interpolation สำหรับค่าที่ไม่อยู่ในตาราง
            zr = -1.282  # default ค่า 90%
        
        # คำนวณ ΔPSI
        delta_psi = initial_psi - terminal_psi
        
        # คำนวณ log(MR)
        log_mr = math.log10(subgrade_mr)
        
        # สมการ AASHTO 1993 สำหรับการหา SN
        # log10(W18) = ZR*S0 + 9.36*log10(SN+1) - 0.20 + log10(ΔPSI/(4.2-1.5))/(0.40+1094/(SN+1)^5.19) + 2.32*log10(MR) - 8.07
        
        # ใช้วิธี iteration เพื่อหา SN
        sn_initial = 3.0  # ค่าเริ่มต้น
        tolerance = 0.01
        max_iterations = 100
        
        for i in range(max_iterations):
            # คำนวณด้านซ้ายของสมการ
            left_side = math.log10(w18)
            
            # คำนวณด้านขวาของสมการ
            term1 = zr * overall_standard_deviation
            term2 = 9.36 * math.log10(sn_initial + 1) - 0.20
            term3_numerator = math.log10(delta_psi / (4.2 - 1.5))
            term3_denominator = 0.40 + 1094 / ((sn_
