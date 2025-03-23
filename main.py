_Ah = '[yellow]暂无[/yellow]'
_Ag = '[red]无[/red]'
_Af = 'BRN统计'
_Ae = '设置延迟'
_Ad = '设置金额'
_Ac = '%H:%M:%S %d-%m-%Y'
_Ab = '平均每笔交易'
_Aa = '交易次数'
_AZ = '总估算价值'
_AY = '总估算BRN'
_AX = '[bold red]无效选项。[/bold red]'
_AW = '[bold red]无效延迟值。[/bold red]'
_AV = '选择一个选项 (1-3) 或按回车键返回'
_AU = '[bold red]无效选择。[/bold red]'
_AT = '[bold red]无效选择。请选1-3。[/bold red]'
_AS = 'Arbitrum - OP'
_AR = 'OP - Arbitrum'
_AQ = 'Arbitrum - BASE'
_AP = 'BASE - Arbitrum'
_AO = 'BASE - OP'
_AN = 'OP - BASE'
_AM = 'data_bridge'
_AL = '参数'
_AK = 'estimated_received_eth'
_AJ = 'brn_bonus_usd'
_AI = 'confirmed'
_AH = '估算BRN'
_AG = '状态'
_AF = '账户'
_AE = 'expiry'
_AD = '自定义延迟'
_AC = 'right'
_AB = '[bold red]延迟不能为负数。[/bold red]'
_AA = 'bridge_amount'
_A9 = '网络'
_A8 = 'total_brn_with_bonus'
_A7 = 'bonus_brn'
_A6 = 'base_brn_bonus'
_A5 = 'Asia/Jakarta'
_A4 = 'bonus'
_A3 = 'estimate'
_A2 = 'explorer'
_A1 = 'block'
_A0 = 'pending'
_z = 'install'
_y = 'pip'
_x = '桥接'
_w = 'delays'
_v = 'ether'
_u = 'total_usd'
_t = '%d-%m-%Y'
_s = 'balance'
_r = 'red'
_q = '值'
_p = 'latest'
_o = 'blue'
_n = '[bold red]无效输入。[/bold red]'
_m = 'yellow'
_l = 'avg_usd'
_k = 'number'
_j = 'rpc_url'
_i = 'access'
_h = 'wallet'
_g = 'magenta'
_f = 'nonce'
_e = '默认'
_d = 'between_cycles'
_c = 'between_bridges'
_b = 'between_accounts'
_a = 'w'
_Z = 'total_brn'
_Y = 'bonus_percentage'
_X = 'avg_brn'
_W = 'gas'
_V = 'Base Sepolia'
_U = 'OP Sepolia'
_T = 'Arbitrum Sepolia'
_S = 'config.json'
_R = False
_Q = 'transaction_count'
_P = 'brn'
_O = 'bridge'
_N = 'info'
_M = 'success'
_L = True
_K = 'time'
_J = '🔵'
_I = 'transactions'
_H = 'warning'
_G = 'error'
_F = 'custom_delays'
_E = 'settings'
_D = 'bridges'
_C = 'cyan'
_B = None
_A = 'green'
import time, os, sys, logging, binascii, json, re, threading
from typing import Dict, List, Tuple, Optional, Any, Union
from web3 import Web3
from web3.exceptions import TransactionNotFound
from eth_account import Account
from eth_account.signers.local import LocalAccount
from datetime import datetime, timedelta
from decimal import Decimal
try:
    import pytz, requests
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
    from rich.prompt import Prompt, Confirm
    from rich.live import Live
    from rich.layout import Layout
    from rich.text import Text
    from rich.box import ROUNDED, HEAVY, DOUBLE
except ImportError:
    print('正在安装所需包...')
    import subprocess
    subprocess.check_call([sys.executable, '-m', _y, _z, 'rich'])
    subprocess.check_call([sys.executable, '-m', _y, _z, 'pytz'])
    subprocess.check_call([sys.executable, '-m', _y, _z, 'requests'])
    import pytz
    import requests
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
    from rich.prompt import Prompt, Confirm
    from rich.live import Live
    from rich.layout import Layout
    from rich.text import Text
    from rich.box import ROUNDED, HEAVY, DOUBLE
console = Console()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler('t3rn_bot.log'), logging.StreamHandler()])
logger = logging.getLogger('t3rn-bot')
CHAIN_STYLES = {_T: (_o, _J), _U: (_r, '🔴'), _V: (_C, _J)}
STATUS_ICONS = {
    _M: '✅',  # 成功
    _G: '❌',  # 错误
    _H: '⚠️',  # 警告
    _N: 'ℹ️',  # 信息
    _A0: '⏳',  # 待处理
    _AI: '✓',  # 已确认
    _s: '💰',  # 余额
    'network': '🌐',  # 网络
    _O: '🌉',  # 桥接
    _W: '⛽',  # Gas费用
    _K: '⏱️',  # 时间
    _A1: '🧱',  # 区块
    _h: '👛',  # 钱包
    'key': '🔑',  # 密钥
    _E: '⚙️',  # 设置
    _f: '🔢',  # Nonce
    _A2: '🔍',  # 浏览器
    _i: '🔐',  # 访问权限
    _P: '🪙',  # BRN代币
    _A3: '📊',  # 估算
    _A4: '🎁'   # 奖励
}

def get_user_ip():
    """获取用户的公共IP地址"""
    try:
        A = requests.get('https://api.ipify.org', timeout=5)
        if A.status_code == 200:
            return A.text.strip()
        else:
            logger.error(f"获取IP错误: HTTP {A.status_code}")
            return
    except Exception as B:
        logger.error(f"获取用户IP错误: {B}")
        return

def fetch_whitelist():
    """从GitHub获取并解析IP白名单"""
    B = {}
    try:
        H = 'https://raw.githubusercontent.com/YoaTzy/ip-whitelist/refs/heads/main/allow'
        C = requests.get(H, timeout=10)
        if C.status_code != 200:
            logger.error(f"获取白名单错误: HTTP {C.status_code}")
            return B
        for A in C.text.splitlines():
            A = A.strip()
            if not A or A.startswith('#'):
                continue
            D = A.split()
            if len(D) >= 2:
                F = D[0]
                G = D[1]
                try:
                    I = datetime.strptime(G, _t)
                    B[F] = I
                except ValueError as E:
                    logger.warning(f"IP {F} 的日期格式无效: {G} - {E}")
        return B
    except Exception as E:
        logger.error(f"获取白名单错误: {E}")
        return B

def check_ip_access(ip):
    """
    检查IP是否在白名单中允许访问
    
    返回:
        元组 (是否允许, 过期时间, 消息)
    """
    if not ip:
        return _R, _B, '无法确定您的IP地址'
    B = fetch_whitelist()
    D = pytz.timezone(_A5)
    C = datetime.now(D).replace(tzinfo=_B)
    if ip in B:
        A = B[ip]
        if A > C:
            return _L, A, f"访问权限有效至 {A.strftime(_t)}"
        else:
            return _R, _B, f"您的IP访问权限已于 {A.strftime(_t)} 到期"
    else:
        E = C + timedelta(hours=1)
        return _R, E, f"IP不在白名单中。授予1小时试用。"

def load_config():
    """从config.json文件加载配置"""
    try:
        with open(_S, 'r') as A:
            return json.load(A)
    except FileNotFoundError:
        return load_config

class NetworkManager:
    """管理网络连接和RPC端点"""
    def __init__(A, config):
        B = config
        A.networks = B['networks']
        A.alternative_rpcs = B['alternative_rpcs']
        A.explorer_urls = B[_E]['explorer_urls']
        A.web3_connections = {}

    def get_web3(B, network_name):
        """为指定网络获取web3连接，如有需要尝试多个RPC"""
        A = network_name
        if A in B.web3_connections:
            C = B.web3_connections[A]
            try:
                if C.is_connected():
                    C.eth.block_number
                    return C
            except Exception:
                pass
        F = B.networks[A][_j]
        C = B._try_rpc(A, F)
        if C:
            B.web3_connections[A] = C
            return C
        if A in B.alternative_rpcs:
            with Progress(SpinnerColumn(), TextColumn('[bold blue]尝试备用RPC...'), console=console) as D:
                G = D.add_task('', total=len(B.alternative_rpcs[A]))
                for E in B.alternative_rpcs[A]:
                    if E == F:
                        D.advance(G)
                        continue
                    C = B._try_rpc(A, E)
                    D.advance(G)
                    if C:
                        B.networks[A][_j] = E
                        B.web3_connections[A] = C
                        return C
        console.print(f"[bold red]{STATUS_ICONS[_G]} {A} 的所有RPC端点均失败！[/bold red]")

    def _try_rpc(P, network_name, rpc_url):
        """尝试连接到RPC端点，带超时处理"""
        F = 'timestamp'
        C = rpc_url
        A = network_name
        try:
            console.print(f"[cyan]{STATUS_ICONS[_N]} 尝试 {A} 的RPC: {C}[/cyan]")
            D = Web3(Web3.HTTPProvider(C, request_kwargs={'timeout': 5}))
            K = 5
            L = time.time()
            G = _R
            while time.time() - L < K:
                try:
                    if D.is_connected():
                        G = _L
                        break
                except Exception:
                    time.sleep(.5)
            if not G:
                console.print(f"[yellow]{STATUS_ICONS[_H]} {A} 连接超时[/yellow]")
                return
            try:
                console.print(f"[cyan]检查 {A} 健康状态...[/cyan]")
                H = threading.Event()
                B = {_k: _B, F: _B, _M: _R}
                def M():
                    try:
                        A = D.eth.block_number
                        C = D.eth.get_block(_p)
                        B[_k] = A
                        B[F] = C.timestamp
                        B[_M] = _L
                    except Exception as E:
                        console.print(f"[yellow]{STATUS_ICONS[_H]} 获取区块失败: {E}[/yellow]")
                    finally:
                        H.set()
                I = threading.Thread(target=M)
                I.daemon = _L
                I.start()
                if not H.wait(timeout=5):
                    console.print(f"[yellow]{STATUS_ICONS[_H]} {A} 的区块数据获取超时[/yellow]")
                    return
                if B[_M]:
                    N = B[_k]
                    O = int(time.time())
                    J = O - B[F]
                    if J > 300:
                        console.print(f"[yellow]{STATUS_ICONS[_H]} 警告: {A} 最新区块已有 {J} 秒未更新。[/yellow]")
                    console.print(f"[green]{STATUS_ICONS[_M]} 已连接到 {A} 的 {C} (区块: {N})[/green]")
                    return D
                else:
                    return
            except Exception as E:
                console.print(f"[yellow]{STATUS_ICONS[_H]} 健康检查失败: {E}[/yellow]")
                return
        except Exception as E:
            console.print(f"[yellow]{STATUS_ICONS[_H]} RPC失败: {C} - {E}[/yellow]")

    def get_explorer_url(A, network_name, tx_hash):
        """获取交易的浏览器URL"""
        B = A.explorer_urls.get(network_name, '')
        return f"{B}{tx_hash}"

class BRNEstimator:
    """估算桥接交易的BRN奖励"""
    def __init__(A):
        A.api_url = 'https://api.t2rn.io/estimate'
        A.chain_codes = {_T: 'arbt', _U: 'opst', _V: 'bast'}
        A.total_estimated_brn = 0
        A.total_estimated_usd = Decimal('0')
        A.transaction_count = 0
        A.bonus_percentage = 50

    def estimate_brn(A, from_chain, to_chain, amount_eth):
        """估算从某链到另一链的BRN奖励"""
        S = '100'
        R = '0x0'
        Q = 'hex'
        P = 'eth'
        H = to_chain
        G = from_chain
        try:
            I = A.chain_codes.get(G)
            J = A.chain_codes.get(H)
            if not I or not J:
                logger.error(f"未知链名: {G} -> {H}")
                return
            T = int(amount_eth * 10**18)
            U = {'amountWei': str(T), 'executorTipUSD': 0, 'fromAsset': P, 'fromChain': I, 'overpayOptionPercentage': 0, 'spreadOptionPercentage': 0, 'toAsset': P, 'toChain': J}
            console.print(f"[cyan]{STATUS_ICONS[_A3]} 正在估算BRN奖励...[/cyan]")
            B = requests.post(A.api_url, json=U, timeout=10)
            if B.status_code == 200:
                C = B.json()
                V = int(C.get('BRNBonusWei', {}).get(Q, R), 16)
                K = Decimal(C.get('BRNBonusUSD', '0'))
                W = int(C.get('estimatedReceivedAmountWei', {}).get(Q, R), 16)
                X = W / 10**18
                L = V / 10**18
                D = Decimal(str(L))
                M = Decimal(str(A.bonus_percentage))
                N = Decimal('1') + M / Decimal(S)
                Y = D * (M / Decimal(S))
                E = D * N
                F = K * N
                A.total_estimated_brn += float(E)
                A.total_estimated_usd += F
                A.transaction_count += 1
                console.print(f"[green]{STATUS_ICONS[_P]} 估算BRN奖励: {L:.8f} BRN +{A.bonus_percentage}% 奖励 = {float(E):.8f} BRN (${F})[/green]")
                return {_A6: float(D), _Y: A.bonus_percentage, _A7: float(Y), _A8: float(E), _AJ: K, 'total_usd_with_bonus': F, _AK: X, 'full_response': C}
            else:
                logger.error(f"API错误: {B.status_code} - {B.text}")
                console.print(f"[yellow]{STATUS_ICONS[_H]} 估算BRN奖励失败: API返回状态 {B.status_code}[/yellow]")
                return
        except Exception as O:
            logger.error(f"估算BRN错误: {O}")
            console.print(f"[yellow]{STATUS_ICONS[_H]} 估算BRN奖励失败: {O}[/yellow]")
            return

    def get_total_estimated_brn(A):
        """获取迄今为止的总估算BRN（包括奖励）"""
        return A.total_estimated_brn

    def get_total_estimated_usd(A):
        """获取迄今为止BRN的总估算美元价值（包括奖励）"""
        return A.total_estimated_usd

    def get_stats(A):
        """获取BRN奖励统计信息（包括奖励）"""
        B = 0
        C = Decimal('0')
        if A.transaction_count > 0:
            B = A.total_estimated_brn / A.transaction_count
            C = A.total_estimated_usd / A.transaction_count
        return {_Z: A.total_estimated_brn, _u: A.total_estimated_usd, _Q: A.transaction_count, _X: B, _l: C, _Y: A.bonus_percentage}

class TransactionManager:
    """管理交易的创建、签名和监控"""
    def __init__(A, network_manager):
        A.network_manager = network_manager
        A.address_nonces = {}
        A.successful_txs = 0

    def get_nonce(B, web3, address, force_refresh=_R):
        """
        获取地址的下一个nonce
        
        参数:
            web3: Web3实例
            address: 账户地址
            force_refresh: 如果为True，总是从区块链获取最新nonce
            
        返回:
            该地址的当前nonce
        """
        A = address
        if not force_refresh and A in B.address_nonces:
            return B.address_nonces[A]
        try:
            D = web3.eth.get_transaction_count(A, _A0)
            E = web3.eth.get_transaction_count(A, _p)
            C = max(D, E)
            console.print(f"[cyan]{STATUS_ICONS[_f]} 从区块链获取nonce: {C} (待处理: {D}, 最新: {E})[/cyan]")
            B.address_nonces[A] = C
            return C
        except Exception as G:
            logger.error(f"获取 {A} 的nonce错误: {G}")
            if A in B.address_nonces:
                F = B.address_nonces[A]
                console.print(f"[yellow]{STATUS_ICONS[_H]} 使用缓存nonce作为备用: {F}[/yellow]")
                return F
            console.print(f"[yellow]{STATUS_ICONS[_H]} 使用默认nonce 0[/yellow]")
            B.address_nonces[A] = 0
            return 0

    def update_nonce(A, address, nonce):
        """更新地址的缓存nonce"""
        A.address_nonces[address] = nonce

    def decode_error(F, error_data):
        """解码失败交易的错误数据"""
        A = error_data
        if not A or len(A) < 10:
            return '未知错误'
        try:
            if A.startswith('0x08c379a0'):
                C = binascii.unhexlify(A[10:].replace('0x', ''))
                B = 32
                D = int.from_bytes(C[B:B+32], 'big')
                E = C[B+32:B+32+D].decode('utf-8')
                return f"合约错误: {E}"
        except Exception:
            pass
        return f"原始错误: {A}"

    def wait_for_transaction(L, web3, tx_hash, timeout=120):
        """等待交易确认，带超时处理和更好的异常处理"""
        B = tx_hash
        A = timeout
        D = time.time()
        I = D + A
        J = web3.to_hex(B) if not isinstance(B, str) else B
        with Progress(SpinnerColumn(), TextColumn('[bold blue]等待确认...'), BarColumn(), TextColumn('[bold cyan]{task.percentage:.0f}%'), TimeElapsedColumn(), console=console) as C:
            E = C.add_task('', total=A)
            while time.time() < I:
                try:
                    F = web3.eth.get_transaction_receipt(B)
                    if F is not _B:
                        C.update(E, completed=A)
                        return F
                except Exception as G:
                    H = str(G)
                    if 'not found' not in H.lower() and 'not available' not in H.lower():
                        console.print(f"[yellow]{STATUS_ICONS[_H]} 检查交易错误: {G}[/yellow]")
                K = time.time() - D
                C.update(E, completed=min(K, A))
                time.sleep(2)
        console.print(f"[yellow]{STATUS_ICONS[_H]} 交易 {J} 在 {A} 秒后超时[/yellow]")

    def send_bridge_transaction(B, network_name, account, bridge_data, value_eth=.1, max_attempts=3):
        """发送桥接交易，带重试逻辑"""
        o = 'blockNumber'
        n = 'maxPriorityFeePerGas'
        m = 'baseFeePerGas'
        e = account
        d = 'gasPrice'
        c = 'chainId'
        b = 'maxFeePerGas'
        W = max_attempts
        V = 'value'
        U = 'data'
        T = 'to'
        P = network_name
        O = 'gwei'
        L = bridge_data
        H = value_eth
        if not L:
            console.print(f"[bold red]{STATUS_ICONS[_G]} 此路线无可用桥接数据。请更新config.json[/bold red]")
            return _B, _B
        A = B.network_manager.get_web3(P)
        if not A:
            console.print(f"[bold red]{STATUS_ICONS[_G]} 无法连接到 {P}[/bold red]")
            return _B, _B
        M = B.network_manager.networks[P]['contract_address']
        C = e.address
        try:
            p = A.eth.get_balance(C)
            f = A.from_wei(p, _v)
            if f < H + .01:
                console.print(f"[yellow]{STATUS_ICONS[_H]} 余额不足: {f} ETH (至少需要 {H + .01})[/yellow]")
                return _B, _B
        except Exception as E:
            console.print(f"[yellow]{STATUS_ICONS[_H]} 无法检查余额: {E}[/yellow]")
        D = B.get_nonce(A, C, force_refresh=_L)
        Q = A.to_wei(H, _v)
        for g in range(1, W + 1):
            if g > 1:
                console.print(Panel(f"[bold yellow]重试 {g}/{W}[/bold yellow]"))
            D = B.get_nonce(A, C, force_refresh=_L)
            time.sleep(5)
            try:
                try:
                    with console.status('[bold cyan]估算Gas...[/bold cyan]'):
                        h = A.eth.estimate_gas({T: M, 'from': C, U: L, V: Q})
                        R = h + 50000
                    console.print(f"[cyan]{STATUS_ICONS[_W]} Gas估算: {h}[/cyan]")
                except Exception as E:
                    console.print(f"[bold red]{STATUS_ICONS[_G]} Gas估算失败: {E}[/bold red]")
                    if isinstance(E, tuple) and len(E) > 1:
                        q = E[1]
                        r = B.decode_error(q)
                        console.print(f"[bold red]{STATUS_ICONS[_G]} 解码错误: {r}[/bold red]")
                    console.print(f"[yellow]{STATUS_ICONS[_H]} 这通常意味着桥接数据无效、余额不足或合约变更[/yellow]")
                    continue
                try:
                    with console.status('[bold cyan]准备交易...[/bold cyan]'):
                        i = A.eth.get_block(_p)
                        if hasattr(i, m):
                            s = i[m]
                            j = A.to_wei(2, O)
                            t = 2 * s + j
                            G = {_f: D, T: M, V: Q, _W: R, b: t, n: j, c: A.eth.chain_id, U: L}
                        else:
                            u = A.eth.gas_price
                            G = {_f: D, T: M, V: Q, _W: R, d: int(u * 1.1), c: A.eth.chain_id, U: L}
                except Exception as E:
                    console.print(f"[yellow]{STATUS_ICONS[_H]} 获取Gas参数错误: {E}[/yellow]")
                    G = {_f: D, T: M, V: Q, _W: R, d: A.to_wei(30, O), c: A.eth.chain_id, U: L}
                F = Table(title='交易详情', box=ROUNDED, border_style=_C)
                F.add_column(_AL, style=_g)
                F.add_column(_q, style=_C)
                F.add_row(f"{STATUS_ICONS[_O]} 合约", M)
                F.add_row(f"{STATUS_ICONS[_s]} 值", f"{H} ETH")
                F.add_row(f"{STATUS_ICONS[_f]} Nonce", f"{G[_f]}")
                F.add_row(f"{STATUS_ICONS[_W]} Gas限制", f"{R}")
                if b in G:
                    F.add_row(f"{STATUS_ICONS[_W]} 最大费用", f"{A.from_wei(G[b], O)} Gwei")
                    F.add_row(f"{STATUS_ICONS[_W]} 优先费用", f"{A.from_wei(G[n], O)} Gwei")
                else:
                    F.add_row(f"{STATUS_ICONS[_W]} Gas价格", f"{A.from_wei(G[d], O)} Gwei")
                console.print(F)
                with console.status('[bold cyan]签名并发送交易...[/bold cyan]'):
                    v = A.eth.account.sign_transaction(G, e.key)
                    X = A.eth.send_raw_transaction(v.raw_transaction)
                    N = A.to_hex(X)
                console.print(f"[green]{STATUS_ICONS[_M]} 交易已发送: {N}[/green]")
                k = B.network_manager.get_explorer_url(P, N)
                console.print(f"[blue]{STATUS_ICONS[_A2]} 浏览器链接: {k}[/blue]")
                S = B.wait_for_transaction(A, X)
                if S:
                    console.print(Panel(f"[bold green]{STATUS_ICONS[_AI]} 交易已在区块 {S[o]} 中确认[/bold green]"))
                    B.update_nonce(C, D + 1)
                    B.display_account_info(C)
                    B.successful_txs += 1
                    J = Table(title='交易收据', box=ROUNDED, border_style=_A)
                    J.add_column('详情', style=_g)
                    J.add_column(_q, style=_A)
                    J.add_row(f"{STATUS_ICONS[_W]} 已用Gas", f"{S['gasUsed']}")
                    J.add_row(f"{STATUS_ICONS[_A1]} 区块编号", f"{S[o]}")
                    J.add_row(f"{STATUS_ICONS[_A2]} 浏览器", k)
                    console.print(J)
                    return N, H
                else:
                    console.print(f"[yellow]{STATUS_ICONS[_H]} 交易未在超时时间内确认[/yellow]")
                    try:
                        w = A.eth.get_transaction(X)
                        if w:
                            console.print(f"[cyan]{STATUS_ICONS[_N]} 交易仍待处理，可能稍后完成[/cyan]")
                            B.update_nonce(C, D + 1)
                            return N, H
                    except Exception:
                        console.print(f"[yellow]{STATUS_ICONS[_H]} 交易可能已被丢弃[/yellow]")
            except Exception as E:
                K = str(E)
                console.print(f"[bold red]{STATUS_ICONS[_G]} 发送交易错误: {K}[/bold red]")
                if 'nonce too low' in K.lower():
                    try:
                        Y = A.eth.get_transaction_count(C, _A0)
                        B.update_nonce(C, Y)
                        D = Y
                        console.print(f"[cyan]{STATUS_ICONS[_N]} 更新nonce至 {Y} (原值过低)[/cyan]")
                    except Exception as Z:
                        console.print(f"[bold red]{STATUS_ICONS[_G]} 更新nonce错误: {Z}[/bold red]")
                elif 'nonce too high' in K.lower():
                    console.print(f"[yellow]{STATUS_ICONS[_H]} 检测到nonce过高错误。正在重置nonce跟踪。[/yellow]")
                    try:
                        import re
                        l = re.search('state: (\\d+)', K)
                        if l:
                            a = int(l.group(1))
                            console.print(f"[cyan]{STATUS_ICONS[_N]} 使用错误消息中的状态nonce: {a}[/cyan]")
                            D = a
                            B.update_nonce(C, a)
                        else:
                            I = A.eth.get_transaction_count(C, _p)
                            console.print(f"[cyan]{STATUS_ICONS[_N]} 无法解析状态nonce。使用最新nonce: {I}[/cyan]")
                            D = I
                            B.update_nonce(C, I)
                    except Exception as Z:
                        console.print(f"[bold red]{STATUS_ICONS[_G]} 处理nonce过高错误失败: {Z}[/bold red]")
                        try:
                            I = A.eth.get_transaction_count(C, _p)
                            console.print(f"[cyan]{STATUS_ICONS[_N]} 使用最新nonce作为备用: {I}[/cyan]")
                            D = I
                            B.update_nonce(C, I)
                        except Exception:
                            console.print(f"[yellow]{STATUS_ICONS[_H]} 使用nonce 0作为最后手段[/yellow]")
                            D = 0
                            B.update_nonce(C, 0)
                elif 'replacement transaction underpriced' in K.lower():
                    console.print(f"[yellow]{STATUS_ICONS[_H]} 同一nonce的交易待处理，需要更高的Gas价格[/yellow]")
                    B.update_nonce(C, D + 1)
                    D += 1
                elif 'already known' in K.lower():
                    console.print(f"[yellow]{STATUS_ICONS[_H]} 交易已提交[/yellow]")
                    B.update_nonce(C, D + 1)
                    return N, H
                continue
        console.print(Panel(f"[bold red]{STATUS_ICONS[_G]} {W} 次尝试均失败[/bold red]"))
        return _B, _B

    def display_account_info(F, address):
        """显示跨网络的账户余额和BRN信息"""
        G = '暂无'
        B = address
        A = Table(title=f"{STATUS_ICONS[_h]} 账户信息: {B[:6]}...{B[-4:]}", box=ROUNDED, border_style=_C)
        A.add_column(_A9, style='bold')
        A.add_column('链ID', style=_C)
        A.add_column('余额', style=_A)
        for C in F.network_manager.networks:
            D = F.network_manager.get_web3(C)
            if D:
                try:
                    H = D.eth.get_balance(B)
                    I = D.from_wei(H, _v)
                    J = D.eth.chain_id
                    N, K = CHAIN_STYLES.get(C, (_A, _J))
                    A.add_row(f"{K} {C}", f"{J}", f"{STATUS_ICONS[_s]} {I:.6f} ETH")
                except Exception as L:
                    A.add_row(f"{C}", G, f"错误: {str(L)[:30]}...")
        try:
            E = Web3(Web3.HTTPProvider('https://b2n.rpc.caldera.xyz/http'))
            if E.is_connected():
                M = E.from_wei(E.eth.get_balance(B), _v)
                A.add_row('🔵 BRN网络', f"{E.eth.chain_id}", f"{STATUS_ICONS[_s]} {M:.6f} BRN")
        except Exception:
            A.add_row('BRN网络', G, '无法连接')
        console.print(A)

class BridgeManager:
    """管理不同网络之间的桥接交易"""
    def __init__(A, config, network_manager, tx_manager):
        B = config
        A.data_bridge = B[_AM]
        A.bridge_amount = B[_E][_AA]
        A.network_manager = network_manager
        A.tx_manager = tx_manager
        A.brn_estimator = BRNEstimator()
        A.bridge_paths = {_AN: (_U, _V), _AO: (_V, _U), _AP: (_V, _T), _AQ: (_T, _V), _AR: (_U, _T), _AS: (_T, _U)}

    def get_available_bridges(A):
        """获取具有有效数据的可用桥接列表"""
        C = []
        for (B, (D, E)) in A.bridge_paths.items():
            if B in A.data_bridge and A.data_bridge[B]:
                C.append((B, f"{D} 到 {E}"))
        return C

    def execute_bridge(B, bridge_name, account, value_eth=_B):
        """执行桥接交易"""
        E = value_eth
        D = bridge_name
        if D not in B.data_bridge or not B.data_bridge[D]:
            console.print(f"[bold red]{STATUS_ICONS[_G]} {D} 无可用桥接数据[/bold red]")
            return _R, _B
        if D not in B.bridge_paths:
            console.print(f"[bold red]{STATUS_ICONS[_G]} 无效桥接名称: {D}[/bold red]")
            return _R, _B
        F, G = B.bridge_paths[D]
        H, J = CHAIN_STYLES.get(F, (_A, _J))
        I, K = CHAIN_STYLES.get(G, (_A, _J))
        console.print(Panel(f"[bold {H}]{J} {F}[/bold {H}] → [bold {I}]{K} {G}[/bold {I}]", title=f"{STATUS_ICONS[_O]} 桥接交易", border_style=_C))
        if E is _B:
            E = B.bridge_amount
        A = B.brn_estimator.estimate_brn(F, G, E)
        if A:
            N = A[_A6]
            O = A[_Y]
            P = A[_A7]
            Q = A[_A8]
            R = A[_AJ]
            S = A[_AK]
            C = Table(title=f"{STATUS_ICONS[_A3]} 交易估算", box=ROUNDED, border_style=_m)
            C.add_column(_AL, style=_g)
            C.add_column(_q, style=_C)
            C.add_row('桥接金额', f"{E} ETH")
            C.add_row('估算接收', f"{S:.6f} ETH")
            C.add_row(f"{STATUS_ICONS[_P]} 基础BRN奖励", f"{N:.8f} BRN")
            C.add_row(f"{STATUS_ICONS[_A4]} 奖励 (+{O}%)", f"[bold green]+{P:.8f} BRN[/bold green]")
            C.add_row(f"{STATUS_ICONS[_P]} 总BRN奖励", f"[bold green]{Q:.8f} BRN (${R})[/bold green]")
            T = B.brn_estimator.get_stats()
            C.add_row(f"{STATUS_ICONS[_P]} 总估算BRN", f"[bold green]{T[_Z]:.8f} BRN[/bold green]")
            console.print(C)
        L, U = B.tx_manager.send_bridge_transaction(F, account, B.data_bridge[D], E)
        if L:
            M = ''
            if A:
                M = f"\n{STATUS_ICONS[_P]} 基础BRN: [green]{A[_A6]:.8f} BRN[/green]\n{STATUS_ICONS[_A4]} 奖励 (+{A[_Y]}%): [green]+{A[_A7]:.8f} BRN[/green]\n{STATUS_ICONS[_P]} 总奖励: [bold green]{A[_A8]:.8f} BRN[/bold green]"
            console.print(Panel(f"[bold green]{STATUS_ICONS[_M]} 桥接交易成功！[/bold green]\n从: [bold {H}]{J} {F}[/bold {H}]\n到: [bold {I}]{K} {G}[/bold {I}]\n金额: {E} ETH{M}", border_style=_A))
            return _L, L
        else:
            console.print(Panel(f"[bold red]{STATUS_ICONS[_G]} 桥接交易失败[/bold red]", border_style=_r))
            return _R, _B

    def get_bridge_delay(A, bridge_name):
        """获取特定桥接的延迟，使用自定义延迟（如已设置）"""
        if hasattr(A, _F) and _D in A.custom_delays:
            return A.custom_delays[_D].get(bridge_name, A.bridge_amount)
        return A.bridge_amount

    def add_custom_bridge(A, source_network, dest_network, bridge_data):
        """添加自定义桥接到配置"""
        F = bridge_data
        E = dest_network
        D = source_network
        B = f"{D} - {E}"
        A.data_bridge[B] = F
        if B not in A.bridge_paths:
            G = next((A for A in A.network_manager.networks if A.startswith(D)), _B)
            H = next((A for A in A.network_manager.networks if A.startswith(E)), _B)
            if G and H:
                A.bridge_paths[B] = G, H
        try:
            with open(_S, 'r') as C:
                I = json.load(C)
            I[_AM][B] = F
            with open(_S, _a) as C:
                json.dump(I, C, indent=2)
            console.print(f"[bold green]{STATUS_ICONS[_M]} 已添加自定义桥接: {B}[/bold green]")
            return _L
        except Exception as J:
            console.print(f"[bold red]{STATUS_ICONS[_G]} 保存自定义桥接失败: {J}[/bold red]")
            return _R

    def get_brn_stats(A):
        """获取BRN奖励统计信息"""
        return A.brn_estimator.get_stats()

class UserInterface:
    """通过命令行界面处理用户交互"""
    def __init__(A, config, network_manager, tx_manager, bridge_manager, accounts, labels, trial_info=_B):
        B = config
        A.config = B
        A.network_manager = network_manager
        A.tx_manager = tx_manager
        A.bridge_manager = bridge_manager
        A.accounts = accounts
        A.labels = labels
        A.bridge_amount = B[_E][_AA]
        A.trial_info = trial_info
        if _w not in B[_E]:
            B[_E][_w] = {_b: 5, _c: 10, _d: 30}
        A.delays = B[_E][_w]
        if _F not in B[_E]:
            B[_E][_F] = {_D: {}, _I: {}}
        A.custom_delays = {_D: B[_E][_F].get(_D, {}), _I: B[_E][_F].get(_I, {})}

    def set_delay_settings(A):
        """设置操作之间及特定桥接/交易的自定义延迟时间"""
        A.clear_screen()
        if _F not in A.config[_E]:
            A.config[_E][_F] = {_D: {}, _I: {}}
        if not hasattr(A, _F):
            A.custom_delays = {_D: A.config[_E][_F].get(_D, {}), _I: A.config[_E][_F].get(_I, {})}
        console.print(Panel(f"[bold cyan]延迟设置:[/bold cyan]\n\n1. 全局延迟\n2. 自定义桥接延迟\n3. 自定义交易延迟", title=f"{STATUS_ICONS[_K]} 延迟设置", border_style=_C))
        C = Prompt.ask('选择要修改的延迟类型 (1-3) 或按回车键返回', default='')
        if not C:
            return
        try:
            B = int(C)
            if B == 1:
                A.set_global_delays()
            elif B == 2:
                A.set_bridge_delays()
            elif B == 3:
                A.set_transaction_delays()
            else:
                console.print(_AT)
                time.sleep(2)
        except ValueError:
            console.print(_AU)
            time.sleep(2)

    def set_global_delays(A):
        """设置全局延迟"""
        A.clear_screen()
        console.print(Panel(f"[bold cyan]当前全局延迟设置:[/bold cyan]\n\n1. 账户之间: {A.delays[_b]} 秒\n2. 桥接之间: {A.delays[_c]} 秒\n3. 周期之间: {A.delays[_d]} 秒", title=f"{STATUS_ICONS[_K]} 全局延迟设置", border_style=_C))
        E = Prompt.ask('选择要修改的延迟 (1-3) 或按回车键返回', default='')
        if not E:
            return
        try:
            C = int(E)
            if C < 1 or C > 3:
                console.print(_AT)
                time.sleep(2)
                return
            G = [_b, _c, _d]
            H = ['账户之间', '桥接之间', '周期之间']
            D = G[C - 1]
            F = H[C - 1]
            I = A.delays[D]
            B = Prompt.ask(f"输入新的 {F} 延迟（秒）", default=str(I))
            try:
                B = int(B)
                if B < 0:
                    console.print(_AB)
                    time.sleep(2)
                    return
                A.delays[D] = B
                A.config[_E][_w][D] = B
                with open(_S, _a) as J:
                    json.dump(A.config, J, indent=2)
                console.print(f"[bold green]✅ {F} 延迟已更新为 {B} 秒[/bold green]")
                time.sleep(2)
            except ValueError:
                console.print('[bold red]无效值。请输入数字。[/bold red]')
                time.sleep(2)
        except (ValueError, IndexError):
            console.print(_AU)
            time.sleep(2)

    def set_bridge_delays(A):
        """设置特定桥接的自定义延迟"""
        P = '[bold red]无效桥接编号。[/bold red]'
        A.clear_screen()
        C = A.bridge_manager.get_available_bridges()
        if not C:
            console.print(f"[bold red]{STATUS_ICONS[_G]} 无可用数据的桥接[/bold red]")
            time.sleep(2)
            return
        E = Table(title='自定义桥接延迟', box=ROUNDED, border_style=_C)
        E.add_column('#', style=_C, justify=_AC)
        E.add_column(_x, style=_g)
        E.add_column(_AD, style=_A)
        for (Q, (B, V)) in enumerate(C, 1):
            I = A.custom_delays[_D].get(B, _e)
            K, L = A.bridge_manager.bridge_paths[B]
            M, R = CHAIN_STYLES.get(K, (_A, _J))
            N, S = CHAIN_STYLES.get(L, (_A, _J))
            T = f"[{M}]{R} {K}[/{M}] → [{N}]{S} {L}[/{N}]"
            E.add_row(str(Q), T, f"{I} 秒" if I != _e else I)
        console.print(E)
        console.print(Panel(f"[bold cyan]选项:[/bold cyan]\n\n1. 为桥接设置自定义延迟\n2. 移除桥接的自定义延迟\n3. 移除所有自定义桥接延迟", title=f"{STATUS_ICONS[_E]} 桥接延迟选项", border_style=_C))
        O = Prompt.ask(_AV, default='')
        if not O:
            return
        try:
            J = int(O)
            if J == 1:
                F = Prompt.ask('输入要设置自定义延迟的桥接编号', default='')
                if not F:
                    return
                try:
                    G = int(F) - 1
                    if 0 <= G < len(C):
                        B = C[G][0]
                        U = A.custom_delays[_D].get(B, A.delays[_c])
                        D = Prompt.ask(f"为此桥接输入自定义延迟（秒）", default=str(U))
                        try:
                            D = int(D)
                            if D < 0:
                                console.print(_AB)
                                time.sleep(2)
                                return
                            A.custom_delays[_D][B] = D
                            if _F not in A.config[_E]:
                                A.config[_E][_F] = {_D: {}, _I: {}}
                            A.config[_E][_F][_D][B] = D
                            with open(_S, _a) as H:
                                json.dump(A.config, H, indent=2)
                            console.print(f"[bold green]✅ {B} 的自定义延迟设置为 {D} 秒[/bold green]")
                            time.sleep(2)
                        except ValueError:
                            console.print(_AW)
                            time.sleep(2)
                    else:
                        console.print(P)
                        time.sleep(2)
                except ValueError:
                    console.print(_n)
                    time.sleep(2)
            elif J == 2:
                F = Prompt.ask('输入要移除自定义延迟的桥接编号', default='')
                if not F:
                    return
                try:
                    G = int(F) - 1
                    if 0 <= G < len(C):
                        B = C[G][0]
                        if B in A.custom_delays[_D]:
                            del A.custom_delays[_D][B]
                            if B in A.config[_E][_F][_D]:
                                del A.config[_E][_F][_D][B]
                                with open(_S, _a) as H:
                                    json.dump(A.config, H, indent=2)
                            console.print(f"[bold green]✅ 已移除 {B} 的自定义延迟[/bold green]")
                        else:
                            console.print(f"[bold yellow]{B} 无自定义延迟[/bold yellow]")
                        time.sleep(2)
                    else:
                        console.print(P)
                        time.sleep(2)
                except ValueError:
                    console.print(_n)
                    time.sleep(2)
            elif J == 3:
                if Confirm.ask('确定要移除所有自定义桥接延迟吗？'):
                    A.custom_delays[_D] = {}
                    A.config[_E][_F][_D] = {}
                    with open(_S, _a) as H:
                        json.dump(A.config, H, indent=2)
                    console.print(f"[bold green]✅ 已移除所有自定义桥接延迟[/bold green]")
                    time.sleep(2)
            else:
                console.print(_AX)
                time.sleep(2)
        except ValueError:
            console.print(_n)
            time.sleep(2)

    def set_transaction_delays(A):
        """设置特定网络上交易的自定义延迟"""
        M = '[bold red]无效网络编号。[/bold red]'
        A.clear_screen()
        D = Table(title='自定义交易延迟', box=ROUNDED, border_style=_C)
        D.add_column('#', style=_C, justify=_AC)
        D.add_column(_A9, style=_g)
        D.add_column(_AD, style=_A)
        E = list(A.network_manager.networks.keys())
        for (N, B) in enumerate(E, 1):
            I = A.custom_delays[_I].get(B, _e)
            K, O = CHAIN_STYLES.get(B, (_A, _J))
            D.add_row(str(N), f"[{K}]{O} {B}[/{K}]", f"{I} 秒" if I != _e else I)
        console.print(D)
        console.print(Panel(f"[bold cyan]选项:[/bold cyan]\n\n1. 为网络设置自定义延迟\n2. 移除网络的自定义延迟\n3. 移除所有自定义交易延迟", title=f"{STATUS_ICONS[_E]} 交易延迟选项", border_style=_C))
        L = Prompt.ask(_AV, default='')
        if not L:
            return
        try:
            J = int(L)
            if J == 1:
                F = Prompt.ask('输入要设置自定义延迟的网络编号', default='')
                if not F:
                    return
                try:
                    G = int(F) - 1
                    if 0 <= G < len(E):
                        B = E[G]
                        P = 5
                        Q = A.custom_delays[_I].get(B, P)
                        C = Prompt.ask(f"输入 {B} 上交易的自定义延迟（秒）", default=str(Q))
                        try:
                            C = int(C)
                            if C < 0:
                                console.print(_AB)
                                time.sleep(2)
                                return
                            A.custom_delays[_I][B] = C
                            if _F not in A.config[_E]:
                                A.config[_E][_F] = {_D: {}, _I: {}}
                            A.config[_E][_F][_I][B] = C
                            with open(_S, _a) as H:
                                json.dump(A.config, H, indent=2)
                            console.print(f"[bold green]✅ {B} 的自定义交易延迟设置为 {C} 秒[/bold green]")
                            time.sleep(2)
                        except ValueError:
                            console.print(_AW)
                            time.sleep(2)
                    else:
                        console.print(M)
                        time.sleep(2)
                except ValueError:
                    console.print(_n)
                    time.sleep(2)
            elif J == 2:
                F = Prompt.ask('输入要移除自定义延迟的网络编号', default='')
                if not F:
                    return
                try:
                    G = int(F) - 1
                    if 0 <= G < len(E):
                        B = E[G]
                        if B in A.custom_delays[_I]:
                            del A.custom_delays[_I][B]
                            if B in A.config[_E][_F][_I]:
                                del A.config[_E][_F][_I][B]
                                with open(_S, _a) as H:
                                    json.dump(A.config, H, indent=2)
                            console.print(f"[bold green]✅ 已移除 {B} 的自定义交易延迟[/bold green]")
                        else:
                            console.print(f"[bold yellow]{B} 无自定义交易延迟[/bold yellow]")
                        time.sleep(2)
                    else:
                        console.print(M)
                        time.sleep(2)
                except ValueError:
                    console.print(_n)
                    time.sleep(2)
            elif J == 3:
                if Confirm.ask('确定要移除所有自定义交易延迟吗？'):
                    A.custom_delays[_I] = {}
                    A.config[_E][_F][_I] = {}
                    with open(_S, _a) as H:
                        json.dump(A.config, H, indent=2)
                    console.print(f"[bold green]✅ 已移除所有自定义交易延迟[/bold green]")
                    time.sleep(2)
            else:
                console.print(_AX)
                time.sleep(2)
        except ValueError:
            console.print(_n)
            time.sleep(2)

    def clear_screen(A):
        """清空终端屏幕"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_network_info(I):
        """显示当前网络信息，带超时保护"""
        Q = '未知'
        E = 'chain_id'
        B = Table(title=f"{STATUS_ICONS['network']} 网络状态", box=ROUNDED, border_style=_o)
        B.add_column(_A9, style='bold')
        B.add_column('链ID', style=_C)
        B.add_column('区块', style=_A)
        B.add_column('RPC端点', style=_o)
        for (A, C) in I.network_manager.networks.items():
            try:
                K = time.time()
                L = 5
                F = _B
                try:
                    F = I.network_manager.get_web3(A)
                    if time.time() - K > L:
                        raise TimeoutError(f"获取 {A} 的web3超时")
                except Exception as G:
                    console.print(f"[yellow]获取 {A} 的web3错误: {G}[/yellow]")
                if F and F.is_connected():
                    try:
                        M = L - (time.time() - K)
                        if M <= 0:
                            raise TimeoutError('网络检查超时')
                        D = {_k: _B, E: _B, _M: _R}
                        N = threading.Event()
                        def R():
                            try:
                                D[_k] = F.eth.block_number
                                D[E] = F.eth.chain_id
                                D[_M] = _L
                            except Exception as A:
                                console.print(f"[yellow]获取区块信息错误: {A}[/yellow]")
                            finally:
                                N.set()
                        O = threading.Thread(target=R)
                        O.daemon = _L
                        O.start()
                        if not N.wait(timeout=min(3, M)):
                            raise TimeoutError('区块数据获取超时')
                        if D[_M]:
                            S = D[_k]
                            T = D[E]
                            J = C[_j]
                            P, H = CHAIN_STYLES.get(A, (_A, _J))
                            B.add_row(f"{H} {A}", f"{T}", f"{STATUS_ICONS[_A1]} {S}", f"{J[:40]}..." if len(J) > 40 else J)
                        else:
                            raise Exception('获取区块数据失败')
                    except Exception as G:
                        B.add_row(f"{A}", f"{C[E]}", f"错误: {str(G)[:30]}...", f"{C[_j][:40]}...")
                else:
                    P, H = CHAIN_STYLES.get(A, (_A, _J))
                    B.add_row(f"{H} {A}", f"{C[E]}", '[red]未连接[/red]', f"{C[_j][:40]}...")
            except Exception as G:
                P, H = CHAIN_STYLES.get(A, (_A, _J))
                B.add_row(f"{H} {A}", f"{C.get(E, Q)}", f"[red]错误: {str(G)[:20]}...[/red]", f"{C.get(_j, Q)[:40]}...")
        I.clear_screen()
        console.print(B)

    def display_account_balances(C):
        """显示第一个账户的余额和BRN奖励信息（含奖励详情）"""
        if not C.accounts:
            console.print(Panel('[yellow]未配置账户。请更新您的config.json文件。[/yellow]'))
            return
        D = C.accounts[0]
        C.tx_manager.display_account_info(D.address)
        B = C.bridge_manager.get_brn_stats()
        if B[_Q] > 0:
            A = Table(title=f"{STATUS_ICONS[_P]} BRN奖励跟踪", box=ROUNDED, border_style=_A)
            A.add_column('指标', style=_g)
            A.add_column(_q, style=_A)
            A.add_row(_AY, f"[bold green]{B[_Z]:.8f} BRN[/bold green]")
            A.add_row(_AZ, f"[bold green]${B[_u]:.4f} USD[/bold green]")
            A.add_row(_Aa, f"{B[_Q]}")
            A.add_row(_Ab, f"{B[_X]:.8f} BRN (${B[_l]:.4f})")
            A.add_row('奖励信息', f"[cyan]所有奖励包含 +{B[_Y]}% 奖励[/cyan]")
            console.print(A)

    def display_brn_stats(D):
        """显示BRN奖励统计信息，含奖励详情"""
        D.clear_screen()
        A = D.bridge_manager.get_brn_stats()
        if A[_Q] == 0:
            console.print(Panel(f"[yellow]尚未估算BRN奖励。请先运行一些桥接交易。[/yellow]", title=f"{STATUS_ICONS[_P]} BRN奖励统计", border_style=_m))
            time.sleep(3)
            return
        B = Table(title=f"{STATUS_ICONS[_P]} BRN奖励统计", box=ROUNDED, border_style=_A)
        B.add_column('指标', style=_g)
        B.add_column(_q, style=_A)
        B.add_row(_AY, f"[bold green]{A[_Z]:.8f} BRN[/bold green]")
        B.add_row(_AZ, f"[bold green]${A[_u]:.4f} USD[/bold green]")
        B.add_row(_Aa, f"{A[_Q]}")
        B.add_row(_Ab, f"{A[_X]:.8f} BRN (${A[_l]:.4f})")
        C = 24 * 3
        E = C * 365
        F = A[_X] * E
        G = A[_l] * E
        B.add_row('每日估算 (@ 3交易/小时)', f"{A[_X] * C:.4f} BRN (${A[_l] * C:.2f})")
        B.add_row('每月估算 (@ 3交易/小时)', f"{A[_X] * C * 30:.4f} BRN (${A[_l] * C * 30:.2f})")
        B.add_row('每年估算 (@ 3交易/小时)', f"[bold green]{F:.4f} BRN (${G:.2f})[/bold green]")
        console.print(B)
        console.print(Panel(f"[cyan]BRN奖励包含每笔交易 +{A[_Y]}% 的奖励。\n这些估算是基于您历史BRN收益（含奖励）每笔交易 {A[_X]:.8f} BRN 计算的。\n实际奖励可能因网络状况、交易量和t3rn协议变化而有所不同。[/cyan]", title='奖励信息', border_style=_o))
        Prompt.ask('\n按回车键返回主菜单', default='')

    def display_main_menu(B):
        """显示主菜单并获取用户选择"""
        if B.trial_info:
            Q = pytz.timezone(_A5)
            R = datetime.now(Q).replace(tzinfo=_B)
            F = B.trial_info[_AE].replace(tzinfo=_B)
            G = F - R
            S, T = divmod(G.total_seconds(), 3600)
            U, V = divmod(T, 60)
            if G.total_seconds() > 0:
                console.print(Panel(f"[bold yellow]您的IP: {B.trial_info['ip']}[/bold yellow]\n试用剩余时间: [bold cyan]{int(S)}小时 {int(U)}分 {int(V)}秒[/bold cyan]\n试用到期时间: {F.strftime(_Ac)} WIB", title=f"{STATUS_ICONS[_i]} 试用访问", border_style=_m))
        try:
            B.display_network_info()
            B.display_account_balances()
        except Exception as W:
            console.print(f"[yellow]加载网络信息时出错: {W}。将以有限数据继续。[/yellow]")
        X = Text(f"{STATUS_ICONS[_O]} T3RN桥接机器人 by Yoake", style='bold cyan')
        H = ''
        for (I, (J, Y)) in enumerate(zip(B.accounts, B.labels)):
            H += f"[bold cyan]{STATUS_ICONS[_h]} {Y}:[/bold cyan] {J.address[:6]}...{J.address[-4:]}\n"
        Z = {_AN: (_U, _V), _AO: (_V, _U), _AP: (_V, _T), _AQ: (_T, _V), _AR: (_U, _T), _AS: (_T, _U)}
        for (K, a) in Z.items():
            if K not in B.bridge_manager.bridge_paths:
                B.bridge_manager.bridge_paths[K] = a
        b = B.bridge_manager.get_available_bridges()
        C = ''
        A = []
        C += '[bold cyan]桥接选项:[/bold cyan]\n'
        for (I, (L, f)) in enumerate(b, 1):
            M, N = B.bridge_manager.bridge_paths[L]
            O, c = CHAIN_STYLES.get(M, (_A, _J))
            P, d = CHAIN_STYLES.get(N, (_A, _J))
            C += f"[bold white]{I}.[/bold white] [{O}]{c} {M}[/{O}] → [{P}]{d} {N}[/{P}]\n"
            A.append(L)
        C += '\n[bold cyan]实用选项:[/bold cyan]\n'
        C += f"[bold white]{len(A)+1}.[/bold white] {STATUS_ICONS[_O]} 重复运行所有交易\n"
        C += f"[bold white]{len(A)+2}.[/bold white] {STATUS_ICONS[_O]} 运行自定义选择的桥接\n"
        C += f"[bold white]{len(A)+3}.[/bold white] {STATUS_ICONS[_E]} 设置桥接金额 (当前: {B.bridge_amount} ETH)\n"
        C += f"[bold white]{len(A)+4}.[/bold white] {STATUS_ICONS[_K]} 设置延迟时间 (操作之间)\n"
        C += f"[bold white]{len(A)+5}.[/bold white] {STATUS_ICONS[_P]} 查看BRN奖励统计\n"
        C += f"[bold white]Q.[/bold white] {STATUS_ICONS[_N]} 退出\n"
        e = f"{H}\n{C}"
        console.print(Panel(e, title=X, border_style=_C, box=DOUBLE))
        E = Prompt.ask('选择一个选项', default='Q')
        if E.isdigit():
            D = int(E)
            if 1 <= D <= len(A):
                return A[D - 1]
            elif D == len(A) + 1:
                return 'RUN_ALL'
            elif D == len(A) + 2:
                return 'CUSTOM'
            elif D == len(A) + 3:
                return _Ad
            elif D == len(A) + 4:
                return _Ae
            elif D == len(A) + 5:
                return _Af
        return E.upper()

    def set_bridge_amount(A):
        """设置桥接金额"""
        A.clear_screen()
        console.print(Panel(f"当前桥接金额: {A.bridge_amount} ETH", title=f"{STATUS_ICONS[_E]} 桥接金额", border_style=_C))
        try:
            B = float(Prompt.ask('输入新的ETH金额', default=str(A.bridge_amount)))
            if B <= 0:
                console.print(f"[bold red]{STATUS_ICONS[_G]} 金额必须大于0[/bold red]")
                time.sleep(2)
                return
            A.bridge_amount = B
            A.bridge_manager.bridge_amount = B
            A.config[_E][_AA] = B
            with open(_S, _a) as C:
                json.dump(A.config, C, indent=2)
            console.print(f"[bold green]{STATUS_ICONS[_M]} 桥接金额已设置为 {A.bridge_amount} ETH[/bold green]")
        except ValueError:
            console.print(f"[bold red]{STATUS_ICONS[_G]} 无效金额[/bold red]")
        time.sleep(2)

    def update_status_table_with_brn(H, status_table, bridge_label, account_label, success, bridge_amount, brn_stats):
        """辅助方法：更新状态表，包含BRN奖励信息"""
        E = success
        A = brn_stats
        if E:
            F = f"[green]{STATUS_ICONS[_M]} 成功 - {bridge_amount} ETH[/green]"
        else:
            F = f"[red]{STATUS_ICONS[_G]} 失败[/red]"
        B = ''
        if A[_Q] > 0:
            if E:
                C = A[_Z]
                if A[_Q] > 1:
                    C = A[_Z] - A[_X] * (A[_Q] - 1)
                D = A[_Y]
                G = C / (1 + D / 100)
                I = G * (D / 100)
                B = f"[green]{G:.6f} +{D}% = {C:.6f}[/green]"
            else:
                B = _Ag
        else:
            B = _Ah
        status_table.add_row(bridge_label, account_label, F, B)

    def display_brn_summary(B, brn_stats):
        """显示BRN奖励概要，含奖励信息"""
        A = brn_stats
        if A[_Q] > 0:
            console.print(Panel(f"总估算BRN奖励: [bold green]{A[_Z]:.8f} BRN[/bold green] (${A[_u]:.4f})\n平均每笔交易: [green]{A[_X]:.8f} BRN[/green]\n奖励: [cyan]所有奖励包含 +{A[_Y]}% 奖励[/cyan]", title=f"{STATUS_ICONS[_P]} BRN奖励概要", border_style=_A))

    def run_custom_bridge_selection(A):
        """运行自定义选择的桥接序列"""
        A.clear_screen()
        console.print(Panel('选择要按顺序运行的桥接', title=f"{STATUS_ICONS[_O]} 自定义桥接选择", border_style=_C))
        O = A.bridge_manager.get_available_bridges()
        if not O:
            console.print(f"[bold red]{STATUS_ICONS[_G]} 无可用数据的桥接[/bold red]")
            time.sleep(2)
            return
        I = Table(title='可用桥接', box=ROUNDED, border_style=_C)
        I.add_column('#', style=_C, justify=_AC)
        I.add_column('路线', style=_A)
        I.add_column(_AD, style=_m)
        for (G, (B, h)) in enumerate(O, 1):
            J, K = A.bridge_manager.bridge_paths[B]
            D, L = CHAIN_STYLES.get(J, (_A, _J))
            E, M = CHAIN_STYLES.get(K, (_A, _J))
            P = _e
            if hasattr(A, _F) and _D in A.custom_delays:
                P = A.custom_delays[_D].get(B, _e)
            S = f"[{D}]{L} {J}[/{D}] → [{E}]{M} {K}[/{E}]"
            I.add_row(str(G), S, f"{P}秒" if P != _e else P)
        console.print(I)
        c = Prompt.ask('输入要运行的桥接编号（用逗号分隔，例如 1,3,4）')
        try:
            d = [int(A.strip()) - 1 for A in c.split(',')]
            F = []
            for T in d:
                if 0 <= T < len(O):
                    F.append(O[T][0])
                else:
                    console.print(f"[yellow]{STATUS_ICONS[_H]} 无效选择: {T+1}[/yellow]")
            if not F:
                console.print(f"[bold red]{STATUS_ICONS[_G]} 未选择有效桥接[/bold red]")
                time.sleep(2)
                return
            Q = Table(title='所选桥接', box=ROUNDED, border_style=_A)
            Q.add_column(_x, style=_A)
            Q.add_column('延迟', style=_m)
            for B in F:
                J, K = A.bridge_manager.bridge_paths[B]
                D, L = CHAIN_STYLES.get(J, (_A, _J))
                E, M = CHAIN_STYLES.get(K, (_A, _J))
                C = A.delays[_c]
                if hasattr(A, _F) and _D in A.custom_delays:
                    C = A.custom_delays[_D].get(B, C)
                S = f"[{D}]{L} {J}[/{D}] → [{E}]{M} {K}[/{E}]"
                Q.add_row(S, f"{C}秒" if C != _e else _e)
            console.print(Q)
            if not Confirm.ask(f"按顺序运行这 {len(F)} 个桥接吗？"):
                return
            R = f"[cyan]延迟:[/cyan]\n- 账户之间: {A.delays[_b]} 秒\n"
            U = []
            if hasattr(A, _F) and _D in A.custom_delays:
                for B in F:
                    if B in A.custom_delays[_D]:
                        U.append(f"- {B}: {A.custom_delays[_D][B]} 秒")
            if U:
                R += f"[cyan]自定义桥接延迟:[/cyan]\n" + '\n'.join(U) + '\n'
            else:
                R += f"- 桥接之间: {A.delays[_c]} 秒\n"
            R += f"- 周期之间: {A.delays[_d]} 秒"
            console.print(Panel(f"正在按顺序运行 {len(F)} 个所选桥接...\n按 Ctrl+C 停止\n\n{R}", title=f"{STATUS_ICONS[_O]} 自定义桥接序列", border_style=_C))
            try:
                V = 0
                while _L:
                    if A.trial_info:
                        A.check_trial_expiry()
                    V += 1
                    console.print(f"[bold cyan]{STATUS_ICONS[_N]} 开始第 {V} 周期[/bold cyan]")
                    H = Table(title=f"第 {V} 周期进度", box=ROUNDED, border_style=_C)
                    H.add_column(_x, style=_C)
                    H.add_column(_AF, style=_C)
                    H.add_column(_AG, style=_A)
                    H.add_column(_AH, style=_A)
                    for B in F:
                        N, W = A.bridge_manager.bridge_paths[B]
                        D, L = CHAIN_STYLES.get(N, (_A, _J))
                        E, M = CHAIN_STYLES.get(W, (_A, _J))
                        e = f"[{D}]{L} {N}[/{D}] → [{E}]{M} {W}[/{E}]"
                        console.print(f"[cyan]{STATUS_ICONS[_O]} 处理桥接: {B} ({N} 到 {W})[/cyan]")
                        for (G, f) in enumerate(A.accounts):
                            Y = A.labels[G] if G < len(A.labels) else f"账户 {G+1}"
                            X = _B
                            if hasattr(A, _F) and _I in A.custom_delays:
                                X = A.custom_delays[_I].get(N)
                            if X is not _B:
                                console.print(f"[cyan]{STATUS_ICONS[_K]} 使用 {N} 的自定义交易延迟: {X}秒[/cyan]")
                            console.print(f"[cyan]{STATUS_ICONS[_h]} 处理账户: {Y}[/cyan]")
                            g, i = A.bridge_manager.execute_bridge(B, f, A.bridge_amount)
                            Z = A.bridge_manager.get_brn_stats()
                            A.update_status_table_with_brn(H, e, Y, g, A.bridge_amount, Z)
                            a = A.delays[_b]
                            if G < len(A.accounts) - 1:
                                console.print(f"[cyan]{STATUS_ICONS[_K]} 在下一个账户前等待 {a} 秒...[/cyan]")
                                time.sleep(a)
                        if B != F[-1]:
                            C = A.delays[_c]
                            if hasattr(A, _F) and _D in A.custom_delays:
                                C = A.custom_delays[_D].get(B, C)
                            console.print(f"[cyan]{STATUS_ICONS[_K]} 在下一个桥接前等待 {C} 秒...[/cyan]")
                            time.sleep(C)
                    console.print(H)
                    A.display_brn_summary(Z)
                    b = A.delays[_d]
                    console.print(f"[bold cyan]{STATUS_ICONS[_K]} 自定义选择周期完成。等待 {b} 秒后再次开始...[/bold cyan]")
                    time.sleep(b)
            except KeyboardInterrupt:
                console.print(f"[yellow]{STATUS_ICONS[_H]} 用户停止[/yellow]")
            except TrialExpiredException:
                console.print(f"[bold red]{STATUS_ICONS[_G]} 试用期已过期[/bold red]")
                time.sleep(3)
                return
        except ValueError:
            console.print(f"[bold red]{STATUS_ICONS[_G]} 无效输入。请输入逗号分隔的数字。[/bold red]")
            time.sleep(2)

    def run_single_bridge(A, bridge_name):
        """持续运行单个桥接"""
        H = bridge_name
        I, J = A.bridge_manager.bridge_paths[H]
        K, S = CHAIN_STYLES.get(I, (_A, _J))
        L, T = CHAIN_STYLES.get(J, (_A, _J))
        console.print(Panel(f"""正在持续运行 [{K}]{S} {I}[/{K}] → [{L}]{T} {J}[/{L}] 桥接...
按 Ctrl+C 停止

[cyan]延迟:[/cyan]
- 账户之间: {A.delays[_b]} 秒
- 周期之间: {A.delays[_d]} 秒""", title=f"{STATUS_ICONS[_O]} 单桥接模式", border_style=_C))
        try:
            E = 0
            while _L:
                if A.trial_info:
                    A.check_trial_expiry()
                E += 1
                console.print(f"[bold cyan]{STATUS_ICONS[_N]} 开始第 {E} 周期[/bold cyan]")
                C = Table(title=f"第 {E} 周期进度", box=ROUNDED, border_style=_C)
                C.add_column(_AF, style=_C)
                C.add_column(_AG, style=_A)
                C.add_column('时间', style=_C)
                C.add_column(_AH, style=_A)
                for (D, U) in enumerate(A.accounts):
                    M = A.labels[D] if D < len(A.labels) else f"账户 {D+1}"
                    V = time.time()
                    console.print(f"[cyan]{STATUS_ICONS[_h]} 处理账户: {M}[/cyan]")
                    N, Z = A.bridge_manager.execute_bridge(H, U, A.bridge_amount)
                    W = time.time()
                    if N:
