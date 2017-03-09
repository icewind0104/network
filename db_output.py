from app import db, models
import sys

op = sys.argv[1]

if op == 'outport':
    with open('./db_output/ips.tb', 'w+') as f:
        for row in models.ips.query.all():
            f.write('%d;%s;%s;%s;%s;%d;%s\n' % (row.addr, row.addr_str, row.user, row.mac or '_', row.device or '_', row.net, row.owner.name))

    with open('./db_output/nets.tb', 'w+') as f:
        for row in models.nets.query.all():
            f.write('%s;%d;%d\n' % (row.name, row.ipstart, row.ipend))

if op == 'import':
    with open('./db_output/nets.tb', 'r') as f:
        for line in f.readlines():
            col = line.split(';')
            name = col[0]
            ipstart = col[1]
            ipend = col[2]
            net = models.nets(name=name, ipstart=ipstart, ipend=ipend)
            db.session.add(net)
            db.session.commit()

    with open('./db_output/ips.tb', 'r') as f:
        for line in f.readlines():
            col = line[:-1].split(';')
            user = col[2]
            net_name = col[6]

            employee = models.employees(name=user, department=net_name)
            try:
                db.session.add(employee)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print('duplicate name %s' % user)

    with open('./db_output/ips.tb', 'r') as f:
        for line in f.readlines():
            col = line[:-1].split(';')
            addr = col[0]
            addr_str = col[1]
            user = col[2]
            mac = col[3] if col[3] != '_' else None
            device = col[4] if col[4] != '_' else None
            net_name = col[6]

            net = models.nets.query.filter_by(name=net_name).first().id
            employee_id = models.employees.query.filter_by(name=user).first().id
            ip = models.ips(addr=addr, addr_str=addr_str, employee_id=employee_id, mac=mac, device=device, net=net)
            db.session.add(ip)
            db.session.commit()
