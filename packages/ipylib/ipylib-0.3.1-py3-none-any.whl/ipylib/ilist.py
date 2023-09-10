
import re



def set_difference(li1, li2):
    """차집합 리스트. li1 - li2"""
    return [e for e in li1 if e not in li2]




def reg_matched(li, pat):
    """http://www.cademuir.eu/blog/2011/10/20/python-searching-for-a-string-within-a-list-list-comprehension/
    """
    r = re.compile(".*("+pat+").*")
    return [m.group(0) for e in li for m in [r.search(e)] if m]
