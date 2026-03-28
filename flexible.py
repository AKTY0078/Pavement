import math

class AASHTO1993:
    def __init__(self):
        self.zr = {50:0, 80:-0.841, 85:-1.037, 90:-1.282, 95:-1.645, 99:-2.326}
    
    def calc_esal(self, aadt, truck_pct, growth, years):
        gf = ((1+growth/100)**years-1)/(growth/100) if growth>0 else years
        return aadt * truck_pct/100 * 365 * gf * 1.5 * 0.5
    
    def calc_sn(self, W18, rel, So, dPSI, MR):
        ZR = self.zr.get(rel, -1.645)
        SN = 3.0
        for _ in range(50):
            calc = ZR*So + 9.36*math.log10(SN+1) - 0.20 + math.log10(dPSI/2.7)/(0.40+1094/(SN+1)**5.19) + 2.32*math.log10(MR) - 8.07
            err = math.log10(W18) - calc
            if abs(err) < 0.001: break
            SN = max(0.1, SN + err*0.5)
        return round(SN, 2)
    
    def calc_thick(self, SN, a1=0.44, a2=0.14, a3=0.11):
        D1 = max(3, SN/(3*a1))
        SN_rem = SN - a1*D1
        D2 = max(6, SN_rem/(2*a2)) if SN_rem>0 else 0
        SN_rem -= a2*D2
        D3 = max(0, SN_rem/a3) if SN_rem>0 else 0
        return {"AC":round(D1,1), "Base":round(D2,1), "Subbase":round(D3,1)}

# ใช้งาน
d = AASHTO1993()
W18 = d.calc_esal(5000, 15, 4, 20)
SN = d.calc_sn(W18, 90, 0.45, 2.0, 10000)
thick = d.calc_thick(SN)
print(f"ESAL: {W18:,.0f}")
print(f"SN: {SN}")
print(f"ความหนา: {thick}")
