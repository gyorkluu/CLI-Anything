import sys
import json

sys.path.insert(0, '/www/server/panel/class')
sys.path.insert(0, '/www/server/panel')

operation = sys.argv[1]
args = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}

try:
    if operation == 'list_sites':
        import public
        data = public.M('sites').field('id,name,status,ps,path,addtime').select()
        print(json.dumps(data if isinstance(data, list) else [], ensure_ascii=False))

    elif operation == 'get_site_info':
        import public
        site = public.M('sites').where('id=?', (args['site_id'],)).find()
        if isinstance(site, str):
            print(json.dumps({'error': 'not found'}, ensure_ascii=False))
        else:
            domains = public.M('domain').where('pid=?', (site['id'],)).select()
            site['domains'] = domains if isinstance(domains, list) else []
            print(json.dumps(site, ensure_ascii=False))

    elif operation == 'create_site':
        import public
        from panelSite import panelSite
        domain = args.get('domain', '')
        port = args.get('port', '80')
        path = args['path']
        version = args.get('version', '00')
        domainlist = args.get('domainlist', [])
        if not domainlist:
            domainlist = [f'{domain}:{port}']
        webname_obj = {
            'domain': domain,
            'domainlist': [d for d in domainlist if d.split(':')[0] != domain],
            'count': 1
        }

        check_name = domain.replace('[', '').replace(']', '')
        if not public.is_ipv6(check_name):
            check_name = check_name.strip().split(':')[0].lower()

        existing = public.M('domain').where("name=? and port=?", (check_name, int(port))).getField('pid')
        if existing:
            site_data = public.M('sites').where('id=?', (existing,)).find()
            if site_data and not (isinstance(site_data, str) and 'error' in site_data):
                print(json.dumps({'status': True, 'msg': '站点已存在', 'id': existing}, ensure_ascii=False))
            else:
                print(json.dumps({'status': False, 'msg': '域名已被占用，但站点记录不存在'}, ensure_ascii=False))
        else:
            site = panelSite()
            get = public.dict_obj()
            get.webname = json.dumps(webname_obj)
            get.path = path
            get.port = port
            get.version = version
            get.type_id = args.get('type_id', '0')
            get.type = 'PHP'
            get.ps = args.get('ps', 'Created via CLI')
            get.ftp = 'true' if args.get('ftp') else False
            get.ftp_username = args.get('ftp_username', '')
            get.ftp_password = args.get('ftp_password', '')
            get.sql = 'true' if args.get('sql') else False
            get.datauser = args.get('datauser', '')
            get.datapassword = args.get('datapassword', '')
            get.codeing = 'utf8'
            result = site.AddSite(get)
            print(json.dumps(result, ensure_ascii=False))

    elif operation == 'delete_site':
        import public
        from panelSite import panelSite
        site_data = public.M('sites').where('id=?', (args['site_id'],)).find()
        if not site_data or (isinstance(site_data, str) and 'error' in site_data):
            print(json.dumps({'status': False, 'msg': '指定站点不存在!'}, ensure_ascii=False))
        else:
            site = panelSite()
            get = public.dict_obj()
            get.id = args['site_id']
            get.webname = site_data.get('name', '')
            result = site.DeleteSite(get)
            print(json.dumps(result, ensure_ascii=False))

    elif operation == 'start_site':
        import public
        from panelSite import panelSite
        site = panelSite()
        get = public.dict_obj()
        get.id = args['site_id']
        result = site.SiteStart(get)
        print(json.dumps(result, ensure_ascii=False))

    elif operation == 'stop_site':
        import public
        from panelSite import panelSite
        site = panelSite()
        get = public.dict_obj()
        get.id = args['site_id']
        result = site.SiteStop(get)
        print(json.dumps(result, ensure_ascii=False))

    elif operation == 'list_domains':
        import public
        domains = public.M('domain').where('pid=?', (args['site_id'],)).select()
        print(json.dumps(domains if isinstance(domains, list) else [], ensure_ascii=False))

    elif operation == 'add_domain':
        import public
        from panelSite import panelSite
        site_data = public.M('sites').where('id=?', (args['site_id'],)).find()
        if not site_data or (isinstance(site_data, str) and 'error' in site_data):
            print(json.dumps({'status': False, 'msg': '指定站点不存在!'}, ensure_ascii=False))
        else:
            site = panelSite()
            get = public.dict_obj()
            get.id = args['site_id']
            get.webname = site_data.get('name', '')
            get.domain = args['domain']
            get.port = args.get('port', '80')
            result = site.AddDomain(get)
            print(json.dumps(result, ensure_ascii=False))

    elif operation == 'list_databases':
        import public
        data = public.M('databases').select()
        print(json.dumps(data if isinstance(data, list) else [], ensure_ascii=False))

    elif operation == 'create_database':
        import public
        from database import database as db_module
        db = db_module()
        get = public.dict_obj()
        get.name = args['name']
        get.username = args['username']
        get.password = args['password']
        get.encoding = args.get('encoding', 'utf8mb4')
        result = db.CreateDatabase(get)
        print(json.dumps(result, ensure_ascii=False))

    elif operation == 'delete_database':
        import public
        from database import database as db_module
        db = db_module()
        get = public.dict_obj()
        get.id = args['db_id']
        result = db.DeleteDatabase(get)
        print(json.dumps(result, ensure_ascii=False))

    elif operation == 'backup_database':
        import public
        from database import database as db_module
        db = db_module()
        get = public.dict_obj()
        get.id = args['db_id']
        result = db.BackupDatabase(get)
        print(json.dumps(result, ensure_ascii=False))

    elif operation == 'list_files':
        import public
        from files import files as files_module
        f = files_module()
        get = public.dict_obj()
        get.path = args['path']
        get.show_sub = '0'
        result = f.GetDir(get)
        print(json.dumps(result, ensure_ascii=False))

    elif operation == 'get_file_body':
        import public
        from files import files as files_module
        f = files_module()
        get = public.dict_obj()
        get.path = args['path']
        result = f.GetFileBody(get)
        print(json.dumps(result, ensure_ascii=False))

    elif operation == 'set_file_body':
        import public
        from files import files as files_module
        f = files_module()
        get = public.dict_obj()
        get.path = args['path']
        get.data = args['content']
        get.encoding = args.get('encoding', 'utf-8')
        result = f.SetFileBody(get)
        print(json.dumps(result, ensure_ascii=False))

    elif operation == 'create_dir':
        import public
        from files import files as files_module
        f = files_module()
        get = public.dict_obj()
        get.path = args['path']
        result = f.CreateDir(get)
        print(json.dumps(result, ensure_ascii=False))

    elif operation == 'delete_path':
        import public
        from files import files as files_module
        f = files_module()
        get = public.dict_obj()
        get.path = args['path']
        result = f.DeleteDir(get)
        print(json.dumps(result, ensure_ascii=False))

    elif operation == 'set_permissions':
        import public
        from files import files as files_module
        f = files_module()
        get = public.dict_obj()
        get.path = args['path']
        get.mode = args['mode']
        get.user = args['user']
        get.group = args['group']
        result = f.SetPermission(get)
        print(json.dumps(result, ensure_ascii=False))

    elif operation == 'get_config':
        import public
        config = public.M('config').where('id=?', (1,)).find()
        if isinstance(config, str) and config.find('error') != -1:
            config = {}
        print(json.dumps(config, ensure_ascii=False))

    elif operation == 'set_panel_port':
        import public
        from config import config as config_module
        c = config_module()
        get = public.dict_obj()
        get.port = args['port']
        result = c.setPanel(get)
        print(json.dumps(result, ensure_ascii=False))

    elif operation == 'set_password':
        import public
        from config import config as config_module
        c = config_module()
        get = public.dict_obj()
        get.password = args['password']
        result = c.setPassword(get)
        print(json.dumps(result, ensure_ascii=False))

    elif operation == 'set_username':
        import public
        from config import config as config_module
        c = config_module()
        get = public.dict_obj()
        get.username = args['username']
        result = c.setUsername(get)
        print(json.dumps(result, ensure_ascii=False))

    elif operation == 'export_sites_json':
        import public
        sites = public.M('sites').select()
        if isinstance(sites, str):
            sites = []
        result = []
        for site in (sites or []):
            domains = public.M('domain').where('pid=?', (site.get('id'),)).select()
            if isinstance(domains, str):
                domains = []
            site['domains'] = domains
            result.append(site)
        print(json.dumps(result, ensure_ascii=False))

    elif operation == 'generate_report':
        import public
        data = {}
        try:
            sr = public.M('sites').select()
            data['sites'] = len(sr) if isinstance(sr, list) else 0
        except Exception:
            data['sites'] = 0
        try:
            dr = public.M('databases').select()
            data['databases'] = len(dr) if isinstance(dr, list) else 0
        except Exception:
            data['databases'] = 0
        try:
            fr = public.M('ftp').select()
            data['ftp_accounts'] = len(fr) if isinstance(fr, list) else 0
        except Exception:
            data['ftp_accounts'] = 0
        print(json.dumps(data, ensure_ascii=False))

    elif operation == 'export_sites_csv':
        import public
        from panelSite import panelSite
        site = panelSite()
        get = public.dict_obj()
        result = site.export_sites_to_csv(get)
        print(json.dumps(result, ensure_ascii=False))

    elif operation == 'read_port':
        port_file = '/www/server/panel/data/port.pl'
        try:
            with open(port_file) as f:
                port = f.read().strip()
            print(json.dumps({'port': port}, ensure_ascii=False))
        except Exception as e:
            print(json.dumps({'port': '8888'}, ensure_ascii=False))

    elif operation == 'read_auth_info':
        auth_file = '/www/server/panel/data/userInfo.json'
        try:
            with open(auth_file) as f:
                data = json.loads(f.read())
            print(json.dumps(data, ensure_ascii=False))
        except Exception:
            print(json.dumps({}, ensure_ascii=False))

    elif operation == 'read_logs':
        log_file = '/www/server/panel/logs/error.log'
        tail_lines = args.get('tail_lines', 100)
        try:
            with open(log_file) as f:
                lines = f.readlines()
            tail = ''.join(lines[-tail_lines:])
            print(json.dumps({'logs': tail}, ensure_ascii=False))
        except Exception as e:
            print(json.dumps({'error': str(e)}, ensure_ascii=False))

    elif operation == 'create_proxy':
        import public
        from panelSite import panelSite
        site = panelSite()
        get = public.dict_obj()
        get.sitename = args['sitename']
        get.proxyname = args.get('proxyname', args['sitename'] + '_proxy')
        get.proxydir = args.get('proxydir', '/')
        get.proxysite = args['proxysite']
        get.todomain = args.get('todomain', args['sitename'])
        get.type = int(args.get('type', 1))
        get.cache = int(args.get('cache', 0))
        get.cachetime = int(args.get('cachetime', 0))
        get.advanced = int(args.get('advanced', 0))
        get.subfilter = json.dumps(args.get('subfilter', [{"sub1": "", "sub2": ""}]))
        get.nocheck = args.get('nocheck', '1')
        result = site.CreateProxy(get)
        print(json.dumps(result, ensure_ascii=False))

    elif operation == 'add_dns_api':
        import public, json, uuid, re
        sfile = '/www/server/panel/config/dns_mager.conf'
        dns_name = args['dns_name']
        pdata = args.get('pdata', {})
        ps = args.get('ps', '')
        new_id = uuid.uuid4().hex
        pdata['id'] = new_id
        pdata['ps'] = ps
        try:
            data = json.loads(public.readFile(sfile))
        except:
            data = {}
        type_data = data.get(dns_name, [])
        type_data.append(pdata)
        data[dns_name] = type_data
        public.writeFile(sfile, json.dumps(data))
        # Link root domains from all sites to this DNS API
        sites = public.M('sites').field('name').select()
        root_domains = set()
        for site in sites:
            name = site.get('name', '')
            parts = name.split('.')
            if len(parts) >= 2:
                root = '.'.join(parts[-2:])
                root_domains.add(root)
        for rd in root_domains:
            existing = public.M('ssl_domains').where('domain=?', (rd,)).count()
            if existing:
                public.M('ssl_domains').where('domain=?', (rd,)).setField('dns_id', new_id)
            else:
                public.M('ssl_domains').add('domain,dns_id,type_id,endtime,ps', (rd, new_id, 0, 0, ''))
        print(json.dumps({'status': True, 'msg': '添加成功', 'id': new_id}, ensure_ascii=False))

    elif operation == 'list_dns_api':
        import public, json
        sfile = '/www/server/panel/config/dns_mager.conf'
        try:
            data = json.loads(public.readFile(sfile))
        except:
            data = {}
        print(json.dumps(data, ensure_ascii=False))

    elif operation == 'apply_ssl':
        import public, json
        from acme_v2 import acme_v2
        acme = acme_v2()
        get = public.dict_obj()
        site_id = args['site_id']
        get.id = site_id
        get.domains = json.dumps(args['domains'])
        get.auth_type = args.get('auth_type', 'dns')
        get.auth_to = args.get('auth_to', '')
        get.auto_wildcard = args.get('auto_wildcard', '0')
        if 'ca' in args:
            get.ca = args['ca']
        result = acme.apply_cert_api(get)
        if result.get('status') and result.get('private_key'):
            from panelSite import panelSite
            site_data = public.M('sites').where('id=?', (site_id,)).find()
            if site_data:
                deploy_get = public.dict_obj()
                deploy_get.siteName = site_data.get('name', '')
                deploy_get.key = result['private_key']
                deploy_get.csr = result['cert'] + '\n' + result.get('root', '')
                deploy_result = panelSite().SetSSL(deploy_get)
                result['deploy'] = deploy_result
        print(json.dumps(result, ensure_ascii=False))

    elif operation == 'get_network_info':
        import subprocess, re
        result = {'ipv4': '', 'ipv6': ''}
        try:
            out = subprocess.check_output(['hostname', '-I'], text=True).strip()
            parts = out.split()
            for p in parts:
                if ':' in p:
                    result['ipv6'] = p
                elif '.' in p:
                    result['ipv4'] = p
        except Exception:
            pass
        if not result['ipv6']:
            try:
                out = subprocess.check_output(['ip', '-6', 'addr', 'show', 'scope', 'global'], text=True)
                m = re.search(r'inet6\s+(\S+)', out)
                if m:
                    result['ipv6'] = m.group(1).split('/')[0]
            except Exception:
                pass
        print(json.dumps(result, ensure_ascii=False))

    elif operation == 'add_dns_record':
        import public
        import os
        import requests as req
        domain = args.get('domain', '')
        subdomain = args.get('subdomain', '')
        record_type = args.get('record_type', 'A')
        value = args.get('value', '')
        ttl = args.get('ttl', 600)
        conf_path = '/www/server/panel/config/dns_mager.conf'
        dns_config = json.loads(public.readFile(conf_path) or '{}')
        dnspod_list = dns_config.get('DNSPodDns', [])
        if not dnspod_list:
            print(json.dumps({'status': False, 'msg': 'No DNSPod credentials configured'}))
            sys.exit(0)
        cred = dnspod_list[0]
        login_token = cred.get('ID', '') + ',' + cred.get('Token', '')
        url = 'https://dnsapi.cn/Record.Create'
        body = {
            'login_token': login_token,
            'format': 'json',
            'domain': domain,
            'sub_domain': subdomain,
            'record_type': record_type,
            'value': value,
            'record_line_id': '0',
            'ttl': ttl,
        }
        resp = req.post(url, data=body, timeout=30).json()
        print(json.dumps(resp, ensure_ascii=False))

    elif operation == 'list_dns_records':
        import public
        import os
        import requests as req
        domain = args.get('domain', '')
        conf_path = '/www/server/panel/config/dns_mager.conf'
        dns_config = json.loads(public.readFile(conf_path) or '{}')
        dnspod_list = dns_config.get('DNSPodDns', [])
        if not dnspod_list:
            print(json.dumps([]))
            sys.exit(0)
        cred = dnspod_list[0]
        login_token = cred.get('ID', '') + ',' + cred.get('Token', '')
        url = 'https://dnsapi.cn/Record.List'
        body = {
            'login_token': login_token,
            'format': 'json',
            'domain': domain,
        }
        resp = req.post(url, data=body, timeout=30).json()
        records = []
        if resp.get('status', {}).get('code') == '1':
            records = [{'id': r['id'], 'name': r['name'], 'type': r['type'], 'value': r['value']} for r in resp.get('records', [])]
        print(json.dumps(records, ensure_ascii=False))

    elif operation == 'delete_dns_record':
        import public
        import os
        import requests as req
        record_id = args.get('record_id', '')
        domain = args.get('domain', '')
        conf_path = '/www/server/panel/config/dns_mager.conf'
        dns_config = json.loads(public.readFile(conf_path) or '{}')
        dnspod_list = dns_config.get('DNSPodDns', [])
        if not dnspod_list:
            print(json.dumps({'status': False, 'msg': 'No DNSPod credentials configured'}))
            sys.exit(0)
        cred = dnspod_list[0]
        login_token = cred.get('ID', '') + ',' + cred.get('Token', '')
        url = 'https://dnsapi.cn/Record.Remove'
        body = {
            'login_token': login_token,
            'format': 'json',
            'domain': domain,
            'record_id': record_id,
        }
        resp = req.post(url, data=body, timeout=30).json()
        print(json.dumps(resp, ensure_ascii=False))

    elif operation == 'set_site_port':
        import public, re
        site_id = str(args.get('site_id', ''))
        port = str(args.get('port', '80'))
        site = public.M('sites').where('id=?', (site_id,)).find()
        if not site:
            print(json.dumps({'status': False, 'msg': 'Site not found'}))
            sys.exit(0)
        site_name = site['name']
        conf_path = '/www/server/panel/vhost/nginx/' + site_name + '.conf'
        conf = public.readFile(conf_path)
        if not conf:
            print(json.dumps({'status': False, 'msg': 'Config not found'}))
            sys.exit(0)
        old_ports = re.findall(r'listen\s+(?:\[::\]:)?(\d+)', conf)
        old_443 = re.findall(r'listen\s+443\s+ssl', conf)
        old_port = old_ports[0] if old_ports else '80'
        conf = conf.replace('listen ' + old_port, 'listen ' + port)
        conf = conf.replace('listen [::]:' + old_port, 'listen [::]:' + port)
        if old_443:
            has_ssl = conf.find('listen ' + port + ' ssl') != -1 or conf.find('listen [::]:' + port + ' ssl') != -1
            if not has_ssl:
                conf = conf.replace('listen ' + port + ';', 'listen ' + port + ' ssl http2 ;')
                conf = conf.replace('listen [::]:' + port + ';', 'listen [::]:' + port + ' ssl http2 ;')
        public.writeFile(conf_path, conf)
        public.M('domain').where('pid=?', (site_id,)).save('port', port)
        public.ExecShell('/www/server/nginx/sbin/nginx -s reload')
        print(json.dumps({'status': True, 'msg': 'Port updated from ' + old_port + ' to ' + port}))

    elif operation == 'add_firewall_port':
        import public, time
        from firewalls import firewalls
        fw = firewalls()
        get = public.dict_obj()
        get.port = str(args.get('port', ''))
        get.ps = str(args.get('ps', ''))
        result = fw.AddAcceptPort(get)
        print(json.dumps(result, ensure_ascii=False))

    elif operation == 'list_firewall_rules':
        import public
        data = public.M('firewall').field('id,port,ps,addtime').select()
        print(json.dumps(data if isinstance(data, list) else [], ensure_ascii=False))

    elif operation == 'delete_firewall_rule':
        import public, time
        from firewalls import firewalls
        fw = firewalls()
        get = public.dict_obj()
        get.id = str(args.get('rule_id', ''))
        result = fw.DelAcceptPort(get)
        print(json.dumps(result, ensure_ascii=False))

    elif operation == 'get_ssl_info':
        import public
        from panelSite import panelSite
        site_id = args.get('site_id', '')
        site = public.M('sites').where('id=?', (site_id,)).find()
        if not site:
            print(json.dumps({'status': False, 'msg': 'Site not found'}))
            sys.exit(0)
        ps = panelSite()
        get = public.dict_obj()
        get.siteName = site['name']
        result = ps.GetSSL(get)
        print(json.dumps(result, ensure_ascii=False))

    elif operation == 'close_ssl':
        import public
        from panelSite import panelSite
        site_id = args.get('site_id', '')
        site = public.M('sites').where('id=?', (site_id,)).find()
        if not site:
            print(json.dumps({'status': False, 'msg': 'Site not found'}))
            sys.exit(0)
        ps = panelSite()
        get = public.dict_obj()
        get.siteName = site['name']
        result = ps.CloseSSLConf(get)
        print(json.dumps(result, ensure_ascii=False))

    elif operation == 'list_cron':
        import public
        data = public.M('crontab').field('id,name,type,where_hour,where_minute,echo,addtime,status,sBody,sType,type_id,second').select()
        if not isinstance(data, list):
            data = []
        print(json.dumps(data, ensure_ascii=False))

    elif operation == 'get_cron':
        import public
        data = public.M('crontab').where('id=?', (args.get('task_id', 0),)).find()
        if isinstance(data, dict) and 'id' in data:
            print(json.dumps(data, ensure_ascii=False))
        else:
            print(json.dumps({'error': 'not found'}, ensure_ascii=False))

    elif operation == 'add_cron':
        import public
        from crontab import crontab as ct
        c = ct()
        get = public.dict_obj()
        get.name = args.get('name', '')
        get.type = args.get('type', 'day')
        get.where1 = int(args.get('where1', 1))
        get.where_hour = int(args.get('where_hour', 3))
        get.where_minute = int(args.get('where_minute', 0))
        get.sBody = args.get('echo_command', '')
        get.sType = 'toShell'
        result = c.AddCrontab(get)
        print(json.dumps(result, ensure_ascii=False))

    elif operation == 'delete_cron':
        import public
        from crontab import crontab as ct
        c = ct()
        get = public.dict_obj()
        get.id = str(args.get('task_id', ''))
        result = c.DelCrontab(get)
        print(json.dumps(result, ensure_ascii=False))

    elif operation == 'set_cron_status':
        import public
        from crontab import crontab as ct
        c = ct()
        get = public.dict_obj()
        get.id = str(args.get('task_id', ''))
        get.status = str(args.get('status', '1'))
        result = c.set_cron_status(get)
        print(json.dumps(result, ensure_ascii=False))

    elif operation == 'add_le_renewal':
        import public
        from crontab import crontab as ct
        c = ct()
        get = public.dict_obj()
        get.name = "续签Let's Encrypt证书"
        get.type = 'day'
        get.where1 = 1
        get.where_hour = 3
        get.where_minute = 0
        get.sBody = '/www/server/panel/pyenv/bin/python3 -u /www/server/panel/class/acme_v2.py --renew=1'
        get.sType = 'toShell'
        if args.get('site_id'):
            get.site_id = str(args['site_id'])
        result = c.AddCrontab(get)
        print(json.dumps(result, ensure_ascii=False))

    else:
        print(json.dumps({'status': False, 'msg': f'Unknown operation: {operation}'}, ensure_ascii=False))

except Exception as e:
    print(json.dumps({'status': False, 'msg': str(e)}, ensure_ascii=False))
