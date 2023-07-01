from bencana.main.submodule.What import What as bencana_What
from bencana.main.submodule.WhoWhereWhen import WhoWhereWhen as bencana_3W
from datetime import datetime
import locale


if __name__ == '__main__':  
    # bencana_what = bencana_What()
    # lst = ['hujan', 'bangunan', 'banjir', 'hujan_BAWWW', 'sungai', 'genangan', 'kemarin', 'banjir', 'pemerintah', 'hujan', 'banjir', 'genangan', 'bandung']
    # q = bencana_what.save_to_mysql(1, lst)
    # print(q)
    bencana_3w = bencana_3W()
    print(bencana_3w.get3W())
    # locale.setlocale(locale.LC_TIME, 'id_ID.UTF-8')
    # x = "Kamis, 15 Des 2022 17:02"
    # print(datetime.strptime(x, "%A, %d %b %Y %H:%M"))
    