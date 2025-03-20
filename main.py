_AJ='SET_DELAYS'
_AI='SET_AMOUNT'
_AH='%H:%M:%S %d-%m-%Y'
_AG='[bold red]Invalid option.[/bold red]'
_AF='[bold red]Invalid delay value.[/bold red]'
_AE='Select an option (1-3) or press Enter to go back'
_AD='[bold red]Invalid choice.[/bold red]'
_AC='[bold red]Invalid choice. Please select 1-3.[/bold red]'
_AB='Arbitrum - OP'
_AA='OP - Arbitrum'
_A9='Arbitrum - BASE'
_A8='BASE - Arbitrum'
_A7='BASE - OP'
_A6='OP - BASE'
_A5='data_bridge'
_A4='confirmed'
_A3='Status'
_A2='Account'
_A1='expiry'
_A0='Custom Delay'
_z='right'
_y='[bold red]Delay cannot be negative.[/bold red]'
_x='bridge_amount'
_w='Network'
_v='Asia/Jakarta'
_u='explorer'
_t='block'
_s='pending'
_r='install'
_q='pip'
_p='yellow'
_o='Bridge'
_n='delays'
_m='magenta'
_l='ether'
_k='%d-%m-%Y'
_j='balance'
_i='red'
_h='blue'
_g='latest'
_f='[bold red]Invalid input.[/bold red]'
_e='number'
_d='rpc_url'
_c='access'
_b='wallet'
_a='nonce'
_Z='Default'
_Y='between_cycles'
_X='between_bridges'
_W='between_accounts'
_V='w'
_U='Base Sepolia'
_T='OP Sepolia'
_S='Arbitrum Sepolia'
_R='gas'
_Q='config.json'
_P=False
_O='bridge'
_N='info'
_M=True
_L='time'
_K='success'
_J='🔵'
_I='transactions'
_H='warning'
_G='error'
_F='custom_delays'
_E='settings'
_D='cyan'
_C='bridges'
_B='green'
_A=None
import time,os,sys,logging,binascii,json,re,threading
from typing import Dict,List,Tuple,Optional,Any,Union
from web3 import Web3
from web3.exceptions import TransactionNotFound
from eth_account import Account
from eth_account.signers.local import LocalAccount
from datetime import datetime,timedelta
try:import pytz,requests;from rich.console import Console;from rich.table import Table;from rich.panel import Panel;from rich.progress import Progress,SpinnerColumn,TextColumn,BarColumn,TimeElapsedColumn;from rich.prompt import Prompt,Confirm;from rich.live import Live;from rich.layout import Layout;from rich.text import Text;from rich.box import ROUNDED,HEAVY,DOUBLE
except ImportError:print('Installing required packages...');import subprocess;subprocess.check_call([sys.executable,'-m',_q,_r,'rich']);subprocess.check_call([sys.executable,'-m',_q,_r,'pytz']);subprocess.check_call([sys.executable,'-m',_q,_r,'requests']);import pytz;import requests;from rich.console import Console;from rich.table import Table;from rich.panel import Panel;from rich.progress import Progress,SpinnerColumn,TextColumn,BarColumn,TimeElapsedColumn;from rich.prompt import Prompt,Confirm;from rich.live import Live;from rich.layout import Layout;from rich.text import Text;from rich.box import ROUNDED,HEAVY,DOUBLE
console=Console()
logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(levelname)s - %(message)s',handlers=[logging.FileHandler('t3rn_bot.log'),logging.StreamHandler()])
logger=logging.getLogger('t3rn-bot')
CHAIN_STYLES={_S:(_h,_J),_T:(_i,'🔴'),_U:(_D,_J)}
STATUS_ICONS={_K:'✅',_G:'❌',_H:'⚠️',_N:'ℹ️',_s:'⏳',_A4:'✓',_j:'💰','network':'🌐',_O:'🌉',_R:'⛽',_L:'⏱️',_t:'🧱',_b:'👛','key':'🔑',_E:'⚙️',_a:'🔢',_u:'🔍',_c:'🔐'}
def get_user_ip():
	"Get the user's public IP address"
	try:
		A=requests.get('https://api.ipify.org',timeout=5)
		if A.status_code==200:return A.text.strip()
		else:logger.error(f"Error getting IP: HTTP {A.status_code}");return
	except Exception as B:logger.error(f"Error getting user IP: {B}");return
def fetch_whitelist():
	'Fetch and parse IP whitelist from GitHub';B={}
	try:
		H='https://raw.githubusercontent.com/YoaTzy/ip-whitelist/refs/heads/main/allow';C=requests.get(H,timeout=10)
		if C.status_code!=200:logger.error(f"Error fetching whitelist: HTTP {C.status_code}");return B
		for A in C.text.splitlines():
			A=A.strip()
			if not A or A.startswith('#'):continue
			D=A.split()
			if len(D)>=2:
				F=D[0];G=D[1]
				try:I=datetime.strptime(G,_k);B[F]=I
				except ValueError as E:logger.warning(f"Invalid date format for IP {F}: {G} - {E}")
		return B
	except Exception as E:logger.error(f"Error fetching whitelist: {E}");return B
def check_ip_access(ip):
	'Check if an IP is allowed based on the whitelist\n    \n    Returns:\n        Tuple of (is_allowed, expiry_time, message)\n    '
	if not ip:return _P,_A,'Could not determine your IP address'
	B=fetch_whitelist();D=pytz.timezone(_v);C=datetime.now(D).replace(tzinfo=_A)
	if ip in B:
		A=B[ip]
		if A>C:return _M,A,f"Access granted until {A.strftime(_k)}"
		else:return _P,_A,f"Your IP access has expired on {A.strftime(_k)}"
	else:E=C+timedelta(hours=1);return _P,E,f"IP not in whitelist. Granting 1-hour trial."
def load_config():
	'Load configuration from config.json file'
	try:
		with open(_Q,'r')as A:return json.load(A)
	except FileNotFoundError:return load_config
class NetworkManager:
	'Manages network connections and RPC endpoints'
	def __init__(A,config):B=config;A.networks=B['networks'];A.alternative_rpcs=B['alternative_rpcs'];A.explorer_urls=B[_E]['explorer_urls'];A.web3_connections={}
	def get_web3(B,network_name):
		'Get a web3 connection for the specified network, trying multiple RPCs if needed';A=network_name
		if A in B.web3_connections:
			C=B.web3_connections[A]
			try:
				if C.is_connected():C.eth.block_number;return C
			except Exception:pass
		F=B.networks[A][_d];C=B._try_rpc(A,F)
		if C:B.web3_connections[A]=C;return C
		if A in B.alternative_rpcs:
			with Progress(SpinnerColumn(),TextColumn('[bold blue]Trying alternative RPCs...'),console=console)as D:
				G=D.add_task('',total=len(B.alternative_rpcs[A]))
				for E in B.alternative_rpcs[A]:
					if E==F:D.advance(G);continue
					C=B._try_rpc(A,E);D.advance(G)
					if C:B.networks[A][_d]=E;B.web3_connections[A]=C;return C
		console.print(f"[bold red]{STATUS_ICONS[_G]} All RPC endpoints failed for {A}![/bold red]")
	def _try_rpc(P,network_name,rpc_url):
		'Try to connect to an RPC endpoint with timeout';F='timestamp';C=rpc_url;A=network_name
		try:
			console.print(f"[cyan]{STATUS_ICONS[_N]} Trying RPC for {A}: {C}[/cyan]");D=Web3(Web3.HTTPProvider(C,request_kwargs={'timeout':5}));K=5;L=time.time();G=_P
			while time.time()-L<K:
				try:
					if D.is_connected():G=_M;break
				except Exception:time.sleep(.5)
			if not G:console.print(f"[yellow]{STATUS_ICONS[_H]} Connection timeout for {A}[/yellow]");return
			try:
				console.print(f"[cyan]Checking {A} health...[/cyan]");H=threading.Event();B={_e:_A,F:_A,_K:_P}
				def M():
					try:A=D.eth.block_number;C=D.eth.get_block(_g);B[_e]=A;B[F]=C.timestamp;B[_K]=_M
					except Exception as E:console.print(f"[yellow]{STATUS_ICONS[_H]} Block retrieval failed: {E}[/yellow]")
					finally:H.set()
				I=threading.Thread(target=M);I.daemon=_M;I.start()
				if not H.wait(timeout=5):console.print(f"[yellow]{STATUS_ICONS[_H]} Block data retrieval timed out for {A}[/yellow]");return
				if B[_K]:
					N=B[_e];O=int(time.time());J=O-B[F]
					if J>300:console.print(f"[yellow]{STATUS_ICONS[_H]} Warning: {A} latest block is {J} seconds old.[/yellow]")
					console.print(f"[green]{STATUS_ICONS[_K]} Connected to {A} at {C} (block: {N})[/green]");return D
				else:return
			except Exception as E:console.print(f"[yellow]{STATUS_ICONS[_H]} Health check failed: {E}[/yellow]");return
		except Exception as E:console.print(f"[yellow]{STATUS_ICONS[_H]} RPC failed: {C} - {E}[/yellow]")
	def get_explorer_url(A,network_name,tx_hash):'Get explorer URL for a transaction';B=A.explorer_urls.get(network_name,'');return f"{B}{tx_hash}"
class TransactionManager:
	'Manages transaction creation, signing, and monitoring'
	def __init__(A,network_manager):A.network_manager=network_manager;A.address_nonces={};A.successful_txs=0
	def get_nonce(B,web3,address,force_refresh=_P):
		'Get the next nonce for an address\n        \n        Args:\n            web3: Web3 instance\n            address: Account address\n            force_refresh: If True, always get fresh nonce from blockchain\n            \n        Returns:\n            Current nonce for the address\n        ';A=address
		if not force_refresh and A in B.address_nonces:return B.address_nonces[A]
		try:D=web3.eth.get_transaction_count(A,_s);E=web3.eth.get_transaction_count(A,_g);C=max(D,E);console.print(f"[cyan]{STATUS_ICONS[_a]} Got nonce from blockchain: {C} (pending: {D}, latest: {E})[/cyan]");B.address_nonces[A]=C;return C
		except Exception as G:
			logger.error(f"Error getting nonce for {A}: {G}")
			if A in B.address_nonces:F=B.address_nonces[A];console.print(f"[yellow]{STATUS_ICONS[_H]} Using cached nonce as fallback: {F}[/yellow]");return F
			console.print(f"[yellow]{STATUS_ICONS[_H]} Using default nonce 0[/yellow]");B.address_nonces[A]=0;return 0
	def update_nonce(A,address,nonce):'Update the cached nonce for an address';A.address_nonces[address]=nonce
	def decode_error(F,error_data):
		'Decode error data from a failed transaction';A=error_data
		if not A or len(A)<10:return'Unknown error'
		try:
			if A.startswith('0x08c379a0'):C=binascii.unhexlify(A[10:].replace('0x',''));B=32;D=int.from_bytes(C[B:B+32],'big');E=C[B+32:B+32+D].decode('utf-8');return f"Contract error: {E}"
		except Exception:pass
		return f"Raw error: {A}"
	def wait_for_transaction(L,web3,tx_hash,timeout=120):
		'Wait for a transaction to be confirmed with timeout and better handling';B=tx_hash;A=timeout;D=time.time();I=D+A;J=web3.to_hex(B)if not isinstance(B,str)else B
		with Progress(SpinnerColumn(),TextColumn('[bold blue]Waiting for confirmation...'),BarColumn(),TextColumn('[bold cyan]{task.percentage:.0f}%'),TimeElapsedColumn(),console=console)as C:
			E=C.add_task('',total=A)
			while time.time()<I:
				try:
					F=web3.eth.get_transaction_receipt(B)
					if F is not _A:C.update(E,completed=A);return F
				except Exception as G:
					H=str(G)
					if'not found'not in H.lower()and'not available'not in H.lower():console.print(f"[yellow]{STATUS_ICONS[_H]} Error checking transaction: {G}[/yellow]")
				K=time.time()-D;C.update(E,completed=min(K,A));time.sleep(2)
		console.print(f"[yellow]{STATUS_ICONS[_H]} Timed out waiting for transaction {J} after {A} seconds[/yellow]")
	def send_bridge_transaction(B,network_name,account,bridge_data,value_eth=.1,max_attempts=3):
		'Send a bridge transaction with retry logic';p='blockNumber';o='Value';n='maxPriorityFeePerGas';m='baseFeePerGas';e='gasPrice';d='chainId';c='maxFeePerGas';X=max_attempts;W=account;V='value';U='data';T='to';P=network_name;O='gwei';L=bridge_data;H=value_eth
		if not L:console.print(f"[bold red]{STATUS_ICONS[_G]} No bridge data available for this route. Please update config.json[/bold red]");return _A,_A
		A=B.network_manager.get_web3(P)
		if not A:console.print(f"[bold red]{STATUS_ICONS[_G]} Cannot connect to {P}[/bold red]");return _A,_A
		M=B.network_manager.networks[P]['contract_address'];C=W.address
		try:
			q=A.eth.get_balance(C);f=A.from_wei(q,_l)
			if f<H+.01:console.print(f"[yellow]{STATUS_ICONS[_H]} Insufficient balance: {f} ETH (need at least {H+.01})[/yellow]");return _A,_A
		except Exception as E:console.print(f"[yellow]{STATUS_ICONS[_H]} Could not check balance: {E}[/yellow]")
		D=B.get_nonce(A,C,force_refresh=_M);Q=A.to_wei(H,_l)
		for g in range(1,X+1):
			if g>1:console.print(Panel(f"[bold yellow]Retry attempt {g}/{X}[/bold yellow]"));D=B.get_nonce(A,C,force_refresh=_M);time.sleep(5)
			try:
				try:
					with console.status('[bold cyan]Estimating gas...[/bold cyan]'):h=A.eth.estimate_gas({T:M,'from':C,U:L,V:Q});R=h+50000
					console.print(f"[cyan]{STATUS_ICONS[_R]} Gas estimate: {h}[/cyan]")
				except Exception as E:
					console.print(f"[bold red]{STATUS_ICONS[_G]} Gas estimation failed: {E}[/bold red]")
					if isinstance(E,tuple)and len(E)>1:r=E[1];s=B.decode_error(r);console.print(f"[bold red]{STATUS_ICONS[_G]} Decoded error: {s}[/bold red]")
					console.print(f"[yellow]{STATUS_ICONS[_H]} This usually means invalid bridge data, insufficient balance, or contract changes[/yellow]");continue
				try:
					with console.status('[bold cyan]Preparing transaction...[/bold cyan]'):
						i=A.eth.get_block(_g)
						if hasattr(i,m):t=i[m];j=A.to_wei(2,O);u=2*t+j;G={_a:D,T:M,V:Q,_R:R,c:u,n:j,d:A.eth.chain_id,U:L}
						else:v=A.eth.gas_price;G={_a:D,T:M,V:Q,_R:R,e:int(v*1.1),d:A.eth.chain_id,U:L}
				except Exception as E:console.print(f"[yellow]{STATUS_ICONS[_H]} Error getting gas parameters: {E}[/yellow]");G={_a:D,T:M,V:Q,_R:R,e:A.to_wei(30,O),d:A.eth.chain_id,U:L}
				F=Table(title='Transaction Details',box=ROUNDED,border_style=_D);F.add_column('Parameter',style=_m);F.add_column(o,style=_D);F.add_row(f"{STATUS_ICONS[_O]} Contract",M);F.add_row(f"{STATUS_ICONS[_j]} Value",f"{H} ETH");F.add_row(f"{STATUS_ICONS[_a]} Nonce",f"{G[_a]}");F.add_row(f"{STATUS_ICONS[_R]} Gas Limit",f"{R}")
				if c in G:F.add_row(f"{STATUS_ICONS[_R]} Max Fee",f"{A.from_wei(G[c],O)} Gwei");F.add_row(f"{STATUS_ICONS[_R]} Priority Fee",f"{A.from_wei(G[n],O)} Gwei")
				else:F.add_row(f"{STATUS_ICONS[_R]} Gas Price",f"{A.from_wei(G[e],O)} Gwei")
				console.print(F)
				with console.status('[bold cyan]Signing and sending transaction...[/bold cyan]'):w=A.eth.account.sign_transaction(G,W.key);Y=A.eth.send_raw_transaction(w.raw_transaction);N=A.to_hex(Y)
				console.print(f"[green]{STATUS_ICONS[_K]} Transaction sent: {N}[/green]");k=B.network_manager.get_explorer_url(P,N);console.print(f"[blue]{STATUS_ICONS[_u]} Explorer link: {k}[/blue]");S=B.wait_for_transaction(A,Y)
				if S:console.print(Panel(f"[bold green]{STATUS_ICONS[_A4]} Transaction confirmed in block {S[p]}[/bold green]"));B.update_nonce(C,D+1);B.display_account_info(W.address);B.successful_txs+=1;J=Table(title='Transaction Receipt',box=ROUNDED,border_style=_B);J.add_column('Detail',style=_m);J.add_column(o,style=_B);J.add_row(f"{STATUS_ICONS[_R]} Gas Used",f"{S['gasUsed']}");J.add_row(f"{STATUS_ICONS[_t]} Block Number",f"{S[p]}");J.add_row(f"{STATUS_ICONS[_u]} Explorer",k);console.print(J);return N,H
				else:
					console.print(f"[yellow]{STATUS_ICONS[_H]} Transaction not confirmed within timeout[/yellow]")
					try:
						x=A.eth.get_transaction(Y)
						if x:console.print(f"[cyan]{STATUS_ICONS[_N]} Transaction still pending, may complete later[/cyan]");B.update_nonce(C,D+1);return N,H
					except Exception:console.print(f"[yellow]{STATUS_ICONS[_H]} Transaction may have been dropped[/yellow]")
			except Exception as E:
				K=str(E);console.print(f"[bold red]{STATUS_ICONS[_G]} Error sending transaction: {K}[/bold red]")
				if'nonce too low'in K.lower():
					try:Z=A.eth.get_transaction_count(C,_s);B.update_nonce(C,Z);D=Z;console.print(f"[cyan]{STATUS_ICONS[_N]} Updated nonce to {Z} (was too low)[/cyan]")
					except Exception as a:console.print(f"[bold red]{STATUS_ICONS[_G]} Error updating nonce: {a}[/bold red]")
				elif'nonce too high'in K.lower():
					console.print(f"[yellow]{STATUS_ICONS[_H]} Nonce too high error detected. Resetting nonce tracking.[/yellow]")
					try:
						import re;l=re.search('state: (\\d+)',K)
						if l:b=int(l.group(1));console.print(f"[cyan]{STATUS_ICONS[_N]} Using state nonce from error message: {b}[/cyan]");D=b;B.update_nonce(C,b)
						else:I=A.eth.get_transaction_count(C,_g);console.print(f"[cyan]{STATUS_ICONS[_N]} Couldn't parse state nonce. Using latest nonce: {I}[/cyan]");D=I;B.update_nonce(C,I)
					except Exception as a:
						console.print(f"[bold red]{STATUS_ICONS[_G]} Error handling nonce too high: {a}[/bold red]")
						try:I=A.eth.get_transaction_count(C,_g);console.print(f"[cyan]{STATUS_ICONS[_N]} Using latest nonce as fallback: {I}[/cyan]");D=I;B.update_nonce(C,I)
						except Exception:console.print(f"[yellow]{STATUS_ICONS[_H]} Using nonce 0 as last resort[/yellow]");D=0;B.update_nonce(C,0)
				elif'replacement transaction underpriced'in K.lower():console.print(f"[yellow]{STATUS_ICONS[_H]} Transaction with same nonce pending, needs higher gas price[/yellow]");B.update_nonce(C,D+1);D+=1
				elif'already known'in K.lower():console.print(f"[yellow]{STATUS_ICONS[_H]} Transaction already submitted[/yellow]");B.update_nonce(C,D+1);return N,H
				continue
		console.print(Panel(f"[bold red]{STATUS_ICONS[_G]} All {X} attempts failed[/bold red]"));return _A,_A
	def display_account_info(F,address):
		'Display account balances across networks and BRN';G='N/A';B=address;A=Table(title=f"{STATUS_ICONS[_b]} Account Information for {B[:6]}...{B[-4:]}",box=ROUNDED,border_style=_D);A.add_column(_w,style='bold');A.add_column('Chain ID',style=_D);A.add_column('Balance',style=_B)
		for C in F.network_manager.networks:
			D=F.network_manager.get_web3(C)
			if D:
				try:H=D.eth.get_balance(B);I=D.from_wei(H,_l);J=D.eth.chain_id;N,K=CHAIN_STYLES.get(C,(_B,_J));A.add_row(f"{K} {C}",f"{J}",f"{STATUS_ICONS[_j]} {I:.6f} ETH")
				except Exception as L:A.add_row(f"{C}",G,f"Error: {str(L)[:30]}...")
		try:
			E=Web3(Web3.HTTPProvider('https://b2n.rpc.caldera.xyz/http'))
			if E.is_connected():M=E.from_wei(E.eth.get_balance(B),_l);A.add_row('🔵 BRN Network',f"{E.eth.chain_id}",f"{STATUS_ICONS[_j]} {M:.6f} BRN")
		except Exception:A.add_row('BRN Network',G,'Could not connect')
		console.print(A)
class BridgeManager:
	'Manages bridge transactions across different networks'
	def __init__(A,config,network_manager,tx_manager):B=config;A.data_bridge=B[_A5];A.bridge_amount=B[_E][_x];A.network_manager=network_manager;A.tx_manager=tx_manager;A.bridge_paths={_A6:(_T,_U),_A7:(_U,_T),_A8:(_U,_S),_A9:(_S,_U),_AA:(_T,_S),_AB:(_S,_T)}
	def get_available_bridges(A):
		'Get list of available bridges with valid data';C=[]
		for(B,(D,E))in A.bridge_paths.items():
			if B in A.data_bridge and A.data_bridge[B]:C.append((B,f"{D} to {E}"))
		return C
	def execute_bridge(A,bridge_name,account,value_eth=_A):
		'Execute a bridge transaction';C=value_eth;B=bridge_name
		if B not in A.data_bridge or not A.data_bridge[B]:console.print(f"[bold red]{STATUS_ICONS[_G]} No bridge data available for {B}[/bold red]");return _P,_A
		if B not in A.bridge_paths:console.print(f"[bold red]{STATUS_ICONS[_G]} Invalid bridge name: {B}[/bold red]");return _P,_A
		D,G=A.bridge_paths[B];E,H=CHAIN_STYLES.get(D,(_B,_J));F,I=CHAIN_STYLES.get(G,(_B,_J));console.print(Panel(f"[bold {E}]{H} {D}[/bold {E}] → [bold {F}]{I} {G}[/bold {F}]",title=f"{STATUS_ICONS[_O]} Bridge Transaction",border_style=_D))
		if C is _A:C=A.bridge_amount
		J,K=A.tx_manager.send_bridge_transaction(D,account,A.data_bridge[B],C)
		if J:console.print(Panel(f"[bold green]{STATUS_ICONS[_K]} Bridge transaction successful![/bold green]\nFrom: [bold {E}]{H} {D}[/bold {E}]\nTo: [bold {F}]{I} {G}[/bold {F}]\nAmount: {C} ETH",border_style=_B));return _M,J
		else:console.print(Panel(f"[bold red]{STATUS_ICONS[_G]} Bridge transaction failed[/bold red]",border_style=_i));return _P,_A
	def get_bridge_delay(A,bridge_name):
		'Get the delay for a specific bridge, using custom delay if set'
		if hasattr(A,_F)and _C in A.custom_delays:return A.custom_delays[_C].get(bridge_name,A.bridge_amount)
		return A.bridge_amount
	def add_custom_bridge(A,source_network,dest_network,bridge_data):
		'Add a custom bridge to the configuration';F=bridge_data;E=dest_network;D=source_network;B=f"{D} - {E}";A.data_bridge[B]=F
		if B not in A.bridge_paths:
			G=next((A for A in A.network_manager.networks if A.startswith(D)),_A);H=next((A for A in A.network_manager.networks if A.startswith(E)),_A)
			if G and H:A.bridge_paths[B]=G,H
		try:
			with open(_Q,'r')as C:I=json.load(C)
			I[_A5][B]=F
			with open(_Q,_V)as C:json.dump(I,C,indent=2)
			console.print(f"[bold green]{STATUS_ICONS[_K]} Added custom bridge: {B}[/bold green]");return _M
		except Exception as J:console.print(f"[bold red]{STATUS_ICONS[_G]} Failed to save custom bridge: {J}[/bold red]");return _P
class UserInterface:
	'Handles user interaction through command line interface'
	def __init__(A,config,network_manager,tx_manager,bridge_manager,accounts,labels,trial_info=_A):
		B=config;A.config=B;A.network_manager=network_manager;A.tx_manager=tx_manager;A.bridge_manager=bridge_manager;A.accounts=accounts;A.labels=labels;A.bridge_amount=B[_E][_x];A.trial_info=trial_info
		if _n not in B[_E]:B[_E][_n]={_W:5,_X:10,_Y:30}
		A.delays=B[_E][_n]
		if _F not in B[_E]:B[_E][_F]={_C:{},_I:{}}
		A.custom_delays={_C:B[_E][_F].get(_C,{}),_I:B[_E][_F].get(_I,{})}
	def set_delay_settings(A):
		'Set custom delay times between operations and for specific bridges/transactions';A.clear_screen()
		if _F not in A.config[_E]:A.config[_E][_F]={_C:{},_I:{}}
		if not hasattr(A,_F):A.custom_delays={_C:A.config[_E][_F].get(_C,{}),_I:A.config[_E][_F].get(_I,{})}
		console.print(Panel(f"[bold cyan]Delay Settings:[/bold cyan]\n\n1. Global Delays\n2. Custom Bridge Delays\n3. Custom Transaction Delays",title=f"{STATUS_ICONS[_L]} Delay Settings",border_style=_D));C=Prompt.ask('Select which delay type to modify (1-3) or press Enter to go back',default='')
		if not C:return
		try:
			B=int(C)
			if B==1:A.set_global_delays()
			elif B==2:A.set_bridge_delays()
			elif B==3:A.set_transaction_delays()
			else:console.print(_AC);time.sleep(2)
		except ValueError:console.print(_AD);time.sleep(2)
	def set_global_delays(A):
		'Set global delay settings';A.clear_screen();console.print(Panel(f"[bold cyan]Current Global Delay Settings:[/bold cyan]\n\n1. Between accounts: {A.delays[_W]} seconds\n2. Between bridges: {A.delays[_X]} seconds\n3. Between cycles: {A.delays[_Y]} seconds",title=f"{STATUS_ICONS[_L]} Global Delay Settings",border_style=_D));E=Prompt.ask('Select which delay to modify (1-3) or press Enter to go back',default='')
		if not E:return
		try:
			C=int(E)
			if C<1 or C>3:console.print(_AC);time.sleep(2);return
			G=[_W,_X,_Y];H=['between accounts','between bridges','between cycles'];D=G[C-1];F=H[C-1];I=A.delays[D];B=Prompt.ask(f"Enter new delay {F} in seconds",default=str(I))
			try:
				B=int(B)
				if B<0:console.print(_y);time.sleep(2);return
				A.delays[D]=B;A.config[_E][_n][D]=B
				with open(_Q,_V)as J:json.dump(A.config,J,indent=2)
				console.print(f"[bold green]✅ {F.title()} delay updated to {B} seconds[/bold green]");time.sleep(2)
			except ValueError:console.print('[bold red]Invalid value. Please enter a number.[/bold red]');time.sleep(2)
		except(ValueError,IndexError):console.print(_AD);time.sleep(2)
	def set_bridge_delays(A):
		'Set custom delays for specific bridges';P='[bold red]Invalid bridge number.[/bold red]';A.clear_screen();C=A.bridge_manager.get_available_bridges()
		if not C:console.print(f"[bold red]{STATUS_ICONS[_G]} No bridges with valid data available[/bold red]");time.sleep(2);return
		E=Table(title='Custom Bridge Delays',box=ROUNDED,border_style=_D);E.add_column('#',style=_D,justify=_z);E.add_column(_o,style=_m);E.add_column(_A0,style=_B)
		for(Q,(B,V))in enumerate(C,1):I=A.custom_delays[_C].get(B,_Z);K,L=A.bridge_manager.bridge_paths[B];M,R=CHAIN_STYLES.get(K,(_B,_J));N,S=CHAIN_STYLES.get(L,(_B,_J));T=f"[{M}]{R} {K}[/{M}] → [{N}]{S} {L}[/{N}]";E.add_row(str(Q),T,f"{I} seconds"if I!=_Z else I)
		console.print(E);console.print(Panel(f"[bold cyan]Options:[/bold cyan]\n\n1. Set custom delay for a bridge\n2. Remove custom delay for a bridge\n3. Remove all custom bridge delays",title=f"{STATUS_ICONS[_E]} Bridge Delay Options",border_style=_D));O=Prompt.ask(_AE,default='')
		if not O:return
		try:
			J=int(O)
			if J==1:
				F=Prompt.ask('Enter bridge number to set custom delay',default='')
				if not F:return
				try:
					G=int(F)-1
					if 0<=G<len(C):
						B=C[G][0];U=A.custom_delays[_C].get(B,A.delays[_X]);D=Prompt.ask(f"Enter custom delay in seconds for this bridge",default=str(U))
						try:
							D=int(D)
							if D<0:console.print(_y);time.sleep(2);return
							A.custom_delays[_C][B]=D
							if _F not in A.config[_E]:A.config[_E][_F]={_C:{},_I:{}}
							A.config[_E][_F][_C][B]=D
							with open(_Q,_V)as H:json.dump(A.config,H,indent=2)
							console.print(f"[bold green]✅ Custom delay for {B} set to {D} seconds[/bold green]");time.sleep(2)
						except ValueError:console.print(_AF);time.sleep(2)
					else:console.print(P);time.sleep(2)
				except ValueError:console.print(_f);time.sleep(2)
			elif J==2:
				F=Prompt.ask('Enter bridge number to remove custom delay',default='')
				if not F:return
				try:
					G=int(F)-1
					if 0<=G<len(C):
						B=C[G][0]
						if B in A.custom_delays[_C]:
							del A.custom_delays[_C][B]
							if B in A.config[_E][_F][_C]:
								del A.config[_E][_F][_C][B]
								with open(_Q,_V)as H:json.dump(A.config,H,indent=2)
							console.print(f"[bold green]✅ Custom delay for {B} removed[/bold green]")
						else:console.print(f"[bold yellow]No custom delay exists for {B}[/bold yellow]")
						time.sleep(2)
					else:console.print(P);time.sleep(2)
				except ValueError:console.print(_f);time.sleep(2)
			elif J==3:
				if Confirm.ask('Are you sure you want to remove all custom bridge delays?'):
					A.custom_delays[_C]={};A.config[_E][_F][_C]={}
					with open(_Q,_V)as H:json.dump(A.config,H,indent=2)
					console.print(f"[bold green]✅ All custom bridge delays removed[/bold green]");time.sleep(2)
			else:console.print(_AG);time.sleep(2)
		except ValueError:console.print(_f);time.sleep(2)
	def set_transaction_delays(A):
		'Set custom delays for transactions on specific networks';M='[bold red]Invalid network number.[/bold red]';A.clear_screen();D=Table(title='Custom Transaction Delays',box=ROUNDED,border_style=_D);D.add_column('#',style=_D,justify=_z);D.add_column(_w,style=_m);D.add_column(_A0,style=_B);E=list(A.network_manager.networks.keys())
		for(N,B)in enumerate(E,1):I=A.custom_delays[_I].get(B,_Z);K,O=CHAIN_STYLES.get(B,(_B,_J));D.add_row(str(N),f"[{K}]{O} {B}[/{K}]",f"{I} seconds"if I!=_Z else I)
		console.print(D);console.print(Panel(f"[bold cyan]Options:[/bold cyan]\n\n1. Set custom delay for a network\n2. Remove custom delay for a network\n3. Remove all custom transaction delays",title=f"{STATUS_ICONS[_E]} Transaction Delay Options",border_style=_D));L=Prompt.ask(_AE,default='')
		if not L:return
		try:
			J=int(L)
			if J==1:
				F=Prompt.ask('Enter network number to set custom delay',default='')
				if not F:return
				try:
					G=int(F)-1
					if 0<=G<len(E):
						B=E[G];P=5;Q=A.custom_delays[_I].get(B,P);C=Prompt.ask(f"Enter custom delay in seconds for transactions on {B}",default=str(Q))
						try:
							C=int(C)
							if C<0:console.print(_y);time.sleep(2);return
							A.custom_delays[_I][B]=C
							if _F not in A.config[_E]:A.config[_E][_F]={_C:{},_I:{}}
							A.config[_E][_F][_I][B]=C
							with open(_Q,_V)as H:json.dump(A.config,H,indent=2)
							console.print(f"[bold green]✅ Custom transaction delay for {B} set to {C} seconds[/bold green]");time.sleep(2)
						except ValueError:console.print(_AF);time.sleep(2)
					else:console.print(M);time.sleep(2)
				except ValueError:console.print(_f);time.sleep(2)
			elif J==2:
				F=Prompt.ask('Enter network number to remove custom delay',default='')
				if not F:return
				try:
					G=int(F)-1
					if 0<=G<len(E):
						B=E[G]
						if B in A.custom_delays[_I]:
							del A.custom_delays[_I][B]
							if B in A.config[_E][_F][_I]:
								del A.config[_E][_F][_I][B]
								with open(_Q,_V)as H:json.dump(A.config,H,indent=2)
							console.print(f"[bold green]✅ Custom transaction delay for {B} removed[/bold green]")
						else:console.print(f"[bold yellow]No custom transaction delay exists for {B}[/bold yellow]")
						time.sleep(2)
					else:console.print(M);time.sleep(2)
				except ValueError:console.print(_f);time.sleep(2)
			elif J==3:
				if Confirm.ask('Are you sure you want to remove all custom transaction delays?'):
					A.custom_delays[_I]={};A.config[_E][_F][_I]={}
					with open(_Q,_V)as H:json.dump(A.config,H,indent=2)
					console.print(f"[bold green]✅ All custom transaction delays removed[/bold green]");time.sleep(2)
			else:console.print(_AG);time.sleep(2)
		except ValueError:console.print(_f);time.sleep(2)
	def clear_screen(A):'Clear the terminal screen';os.system('cls'if os.name=='nt'else'clear')
	def display_network_info(I):
		'Display current network information with timeout protection';Q='Unknown';E='chain_id';B=Table(title=f"{STATUS_ICONS['network']} Network Status",box=ROUNDED,border_style=_h);B.add_column(_w,style='bold');B.add_column('Chain ID',style=_D);B.add_column('Block',style=_B);B.add_column('RPC Endpoint',style=_h)
		for(A,C)in I.network_manager.networks.items():
			try:
				K=time.time();L=5;F=_A
				try:
					F=I.network_manager.get_web3(A)
					if time.time()-K>L:raise TimeoutError(f"Getting web3 for {A} timed out")
				except Exception as G:console.print(f"[yellow]Error getting web3 for {A}: {G}[/yellow]")
				if F and F.is_connected():
					try:
						M=L-(time.time()-K)
						if M<=0:raise TimeoutError('Network check timed out')
						D={_e:_A,E:_A,_K:_P};N=threading.Event()
						def R():
							try:D[_e]=F.eth.block_number;D[E]=F.eth.chain_id;D[_K]=_M
							except Exception as A:console.print(f"[yellow]Error getting block info: {A}[/yellow]")
							finally:N.set()
						O=threading.Thread(target=R);O.daemon=_M;O.start()
						if not N.wait(timeout=min(3,M)):raise TimeoutError('Block data retrieval timed out')
						if D[_K]:S=D[_e];T=D[E];J=C[_d];P,H=CHAIN_STYLES.get(A,(_B,_J));B.add_row(f"{H} {A}",f"{T}",f"{STATUS_ICONS[_t]} {S}",f"{J[:40]}..."if len(J)>40 else J)
						else:raise Exception('Failed to get block data')
					except Exception as G:B.add_row(f"{A}",f"{C[E]}",f"Error: {str(G)[:30]}...",f"{C[_d][:40]}...")
				else:P,H=CHAIN_STYLES.get(A,(_B,_J));B.add_row(f"{H} {A}",f"{C[E]}",'[red]Not connected[/red]',f"{C[_d][:40]}...")
			except Exception as G:P,H=CHAIN_STYLES.get(A,(_B,_J));B.add_row(f"{H} {A}",f"{C.get(E,Q)}",f"[red]Error: {str(G)[:20]}...[/red]",f"{C.get(_d,Q)[:40]}...")
		I.clear_screen();console.print(B)
	def display_account_balances(A):
		'Display balances for the first account'
		if not A.accounts:console.print(Panel('[yellow]No accounts configured. Please update your config.json file.[/yellow]'));return
		B=A.accounts[0];A.tx_manager.display_account_info(B.address)
	def display_main_menu(A):
		'Display the main menu and get user choice'
		if A.trial_info:
			Q=pytz.timezone(_v);R=datetime.now(Q).replace(tzinfo=_A);F=A.trial_info[_A1].replace(tzinfo=_A);G=F-R;S,T=divmod(G.total_seconds(),3600);U,V=divmod(T,60)
			if G.total_seconds()>0:console.print(Panel(f"[bold yellow]Your IP: {A.trial_info['ip']}[/bold yellow]\nTime left in trial: [bold cyan]{int(S)}h {int(U)}m {int(V)}s[/bold cyan]\nTrial expires: {F.strftime(_AH)} WIB",title=f"{STATUS_ICONS[_c]} Trial Access",border_style=_p))
		try:A.display_network_info();A.display_account_balances()
		except Exception as W:console.print(f"[yellow]Error loading network information: {W}. Continuing with limited data.[/yellow]")
		X=Text(f"{STATUS_ICONS[_O]} T3RN Bridge Bot by Yoake",style='bold cyan');H=''
		for(I,(J,Y))in enumerate(zip(A.accounts,A.labels)):H+=f"[bold cyan]{STATUS_ICONS[_b]} {Y}:[/bold cyan] {J.address[:6]}...{J.address[-4:]}\n"
		Z={_A6:(_T,_U),_A7:(_U,_T),_A8:(_U,_S),_A9:(_S,_U),_AA:(_T,_S),_AB:(_S,_T)}
		for(K,a)in Z.items():
			if K not in A.bridge_manager.bridge_paths:A.bridge_manager.bridge_paths[K]=a
		b=A.bridge_manager.get_available_bridges();C='';B=[];C+='[bold cyan]Bridge Options:[/bold cyan]\n'
		for(I,(L,f))in enumerate(b,1):M,N=A.bridge_manager.bridge_paths[L];O,c=CHAIN_STYLES.get(M,(_B,_J));P,d=CHAIN_STYLES.get(N,(_B,_J));C+=f"[bold white]{I}.[/bold white] [{O}]{c} {M}[/{O}] → [{P}]{d} {N}[/{P}]\n";B.append(L)
		C+='\n[bold cyan]Utility Options:[/bold cyan]\n';C+=f"[bold white]{len(B)+1}.[/bold white] {STATUS_ICONS[_O]} Run all transactions repeatedly\n";C+=f"[bold white]{len(B)+2}.[/bold white] {STATUS_ICONS[_O]} Run custom selection of bridges\n";C+=f"[bold white]{len(B)+3}.[/bold white] {STATUS_ICONS[_E]} Set Bridge Amount (current: {A.bridge_amount} ETH)\n";C+=f"[bold white]{len(B)+4}.[/bold white] {STATUS_ICONS[_L]} Set Delay Times (between actions)\n";C+=f"[bold white]Q.[/bold white] {STATUS_ICONS[_N]} Quit\n";e=f"{H}\n{C}";console.print(Panel(e,title=X,border_style=_D,box=DOUBLE));E=Prompt.ask('Choose an option',default='Q')
		if E.isdigit():
			D=int(E)
			if 1<=D<=len(B):return B[D-1]
			elif D==len(B)+1:return'RUN_ALL'
			elif D==len(B)+2:return'CUSTOM'
			elif D==len(B)+3:return _AI
			elif D==len(B)+4:return _AJ
		return E.upper()
	def set_bridge_amount(A):
		'Set the bridge amount';A.clear_screen();console.print(Panel(f"Current bridge amount: {A.bridge_amount} ETH",title=f"{STATUS_ICONS[_E]} Bridge Amount",border_style=_D))
		try:
			B=float(Prompt.ask('Enter new amount in ETH',default=str(A.bridge_amount)))
			if B<=0:console.print(f"[bold red]{STATUS_ICONS[_G]} Amount must be greater than 0[/bold red]");time.sleep(2);return
			A.bridge_amount=B;A.bridge_manager.bridge_amount=B;A.config[_E][_x]=B
			with open(_Q,_V)as C:json.dump(A.config,C,indent=2)
			console.print(f"[bold green]{STATUS_ICONS[_K]} Bridge amount set to {A.bridge_amount} ETH[/bold green]")
		except ValueError:console.print(f"[bold red]{STATUS_ICONS[_G]} Invalid amount[/bold red]")
		time.sleep(2)
	def run_custom_bridge_selection(A):
		'Run a custom selection of bridges in sequence';A.clear_screen();console.print(Panel('Select bridges to run in sequence',title=f"{STATUS_ICONS[_O]} Custom Bridge Selection",border_style=_D));N=A.bridge_manager.get_available_bridges()
		if not N:console.print(f"[bold red]{STATUS_ICONS[_G]} No bridges with valid data available[/bold red]");time.sleep(2);return
		H=Table(title='Available Bridges',box=ROUNDED,border_style=_D);H.add_column('#',style=_D,justify=_z);H.add_column('Route',style=_B);H.add_column(_A0,style=_p)
		for(G,(B,h))in enumerate(N,1):
			I,J=A.bridge_manager.bridge_paths[B];D,K=CHAIN_STYLES.get(I,(_B,_J));F,O=CHAIN_STYLES.get(J,(_B,_J));P=_Z
			if hasattr(A,_F)and _C in A.custom_delays:P=A.custom_delays[_C].get(B,_Z)
			S=f"[{D}]{K} {I}[/{D}] → [{F}]{O} {J}[/{F}]";H.add_row(str(G),S,f"{P}s"if P!=_Z else P)
		console.print(H);c=Prompt.ask('Enter bridge numbers to run (comma separated, e.g. 1,3,4)')
		try:
			d=[int(A.strip())-1 for A in c.split(',')];E=[]
			for T in d:
				if 0<=T<len(N):E.append(N[T][0])
				else:console.print(f"[yellow]{STATUS_ICONS[_H]} Invalid selection: {T+1}[/yellow]")
			if not E:console.print(f"[bold red]{STATUS_ICONS[_G]} No valid bridges selected[/bold red]");time.sleep(2);return
			Q=Table(title='Selected Bridges',box=ROUNDED,border_style=_B);Q.add_column(_o,style=_B);Q.add_column('Delay',style=_p)
			for B in E:
				I,J=A.bridge_manager.bridge_paths[B];D,K=CHAIN_STYLES.get(I,(_B,_J));F,O=CHAIN_STYLES.get(J,(_B,_J));C=A.delays[_X]
				if hasattr(A,_F)and _C in A.custom_delays:C=A.custom_delays[_C].get(B,C)
				S=f"[{D}]{K} {I}[/{D}] → [{F}]{O} {J}[/{F}]";Q.add_row(S,f"{C}s"if C!=_Z else _Z)
			console.print(Q)
			if not Confirm.ask(f"Run these {len(E)} bridges in sequence?"):return
			R=f"[cyan]Delays:[/cyan]\n- Between accounts: {A.delays[_W]} seconds\n";U=[]
			if hasattr(A,_F)and _C in A.custom_delays:
				for B in E:
					if B in A.custom_delays[_C]:U.append(f"- {B}: {A.custom_delays[_C][B]} seconds")
			if U:R+=f"[cyan]Custom Bridge Delays:[/cyan]\n"+'\n'.join(U)+'\n'
			else:R+=f"- Between bridges: {A.delays[_X]} seconds\n"
			R+=f"- Between cycles: {A.delays[_Y]} seconds";console.print(Panel(f"Running {len(E)} selected bridges in sequence...\nPress Ctrl+C to stop\n\n{R}",title=f"{STATUS_ICONS[_O]} Custom Bridge Sequence",border_style=_D))
			try:
				V=0
				while _M:
					if A.trial_info:A.check_trial_expiry()
					V+=1;console.print(f"[bold cyan]{STATUS_ICONS[_N]} Starting cycle {V}[/bold cyan]");L=Table(title=f"Cycle {V} Progress",box=ROUNDED,border_style=_D);L.add_column(_o,style=_D);L.add_column(_A2,style=_D);L.add_column(_A3,style=_B)
					for B in E:
						M,X=A.bridge_manager.bridge_paths[B];D,K=CHAIN_STYLES.get(M,(_B,_J));e=f"[{D}]{K} {M}[/{D}] → [{F}]{O} {X}[/{F}]";console.print(f"[cyan]{STATUS_ICONS[_O]} Processing bridge: {B} ({M} to {X})[/cyan]")
						for(G,f)in enumerate(A.accounts):
							Y=A.labels[G]if G<len(A.labels)else f"Account {G+1}";W=_A
							if hasattr(A,_F)and _I in A.custom_delays:W=A.custom_delays[_I].get(M)
							if W is not _A:console.print(f"[cyan]{STATUS_ICONS[_L]} Using custom transaction delay for {M}: {W}s[/cyan]")
							console.print(f"[cyan]{STATUS_ICONS[_b]} Processing account: {Y}[/cyan]");g,i=A.bridge_manager.execute_bridge(B,f,A.bridge_amount)
							if g:Z=f"[green]{STATUS_ICONS[_K]} Success - {A.bridge_amount} ETH[/green]"
							else:Z=f"[red]{STATUS_ICONS[_G]} Failed[/red]"
							L.add_row(e,Y,Z);a=A.delays[_W]
							if G<len(A.accounts)-1:console.print(f"[cyan]{STATUS_ICONS[_L]} Waiting {a} seconds before next account...[/cyan]");time.sleep(a)
						if B!=E[-1]:
							C=A.delays[_X]
							if hasattr(A,_F)and _C in A.custom_delays:C=A.custom_delays[_C].get(B,C)
							console.print(f"[cyan]{STATUS_ICONS[_L]} Waiting {C} seconds before next bridge...[/cyan]");time.sleep(C)
					console.print(L);b=A.delays[_Y];console.print(f"[bold cyan]{STATUS_ICONS[_L]} Completed custom selection cycle. Waiting {b} seconds before starting again...[/bold cyan]");time.sleep(b)
			except KeyboardInterrupt:console.print(f"[yellow]{STATUS_ICONS[_H]} Stopped by user[/yellow]")
			except TrialExpiredException:console.print(f"[bold red]{STATUS_ICONS[_G]} Trial period has expired[/bold red]");time.sleep(3);return
		except ValueError:console.print(f"[bold red]{STATUS_ICONS[_G]} Invalid input. Please enter comma-separated numbers.[/bold red]");time.sleep(2)
	def run_single_bridge(A,bridge_name):
		'Run a single bridge continuously';E=bridge_name;F,G=A.bridge_manager.bridge_paths[E];H,N=CHAIN_STYLES.get(F,(_B,_J));I,O=CHAIN_STYLES.get(G,(_B,_J));console.print(Panel(f"""Running [{H}]{N} {F}[/{H}] → [{I}]{O} {G}[/{I}] bridge continuously...
Press Ctrl+C to stop

[cyan]Delays:[/cyan]
- Between accounts: {A.delays[_W]} seconds
- Between cycles: {A.delays[_Y]} seconds""",title=f"{STATUS_ICONS[_O]} Single Bridge Mode",border_style=_D))
		try:
			D=0
			while _M:
				if A.trial_info:A.check_trial_expiry()
				D+=1;console.print(f"[bold cyan]{STATUS_ICONS[_N]} Starting cycle {D}[/bold cyan]");B=Table(title=f"Cycle {D} Progress",box=ROUNDED,border_style=_D);B.add_column(_A2,style=_D);B.add_column(_A3,style=_B);B.add_column('Time',style=_D)
				for(C,P)in enumerate(A.accounts):
					J=A.labels[C]if C<len(A.labels)else f"Account {C+1}";Q=time.time();console.print(f"[cyan]{STATUS_ICONS[_b]} Processing account: {J}[/cyan]");R,U=A.bridge_manager.execute_bridge(E,P,A.bridge_amount);S=time.time()
					if R:K=f"[green]{STATUS_ICONS[_K]} Success - {A.bridge_amount} ETH[/green]"
					else:K=f"[red]{STATUS_ICONS[_G]} Failed[/red]"
					T=S-Q;B.add_row(J,K,f"{STATUS_ICONS[_L]} {T:.1f}s");L=A.delays[_W]
					if C<len(A.accounts)-1:console.print(f"[cyan]{STATUS_ICONS[_L]} Waiting {L} seconds before next account...[/cyan]");time.sleep(L)
				console.print(B);M=A.delays[_Y];console.print(f"[bold cyan]{STATUS_ICONS[_L]} Waiting {M} seconds before next cycle...[/bold cyan]");time.sleep(M)
		except KeyboardInterrupt:console.print(f"[yellow]{STATUS_ICONS[_H]} Stopped by user[/yellow]")
		except TrialExpiredException:console.print(f"[bold red]{STATUS_ICONS[_G]} Trial period has expired[/bold red]");time.sleep(3);return
	def run_all_bridges(A):
		'Run all available bridges in sequence';B=f"[cyan]Global Delays:[/cyan]\n- Between accounts: {A.delays[_W]} seconds\n";Y=[]
		if hasattr(A,_F)and _C in A.custom_delays and A.custom_delays[_C]:
			B+=f"[cyan]Custom Bridge Delays:[/cyan]\n"
			for(C,H)in A.custom_delays[_C].items():B+=f"- {C}: {H} seconds\n"
		else:B+=f"- Between bridges: {A.delays[_X]} seconds\n"
		if hasattr(A,_F)and _I in A.custom_delays and A.custom_delays[_I]:
			B+=f"[cyan]Custom Transaction Delays:[/cyan]\n"
			for(S,H)in A.custom_delays[_I].items():B+=f"- {S}: {H} seconds\n"
		B+=f"- Between cycles: {A.delays[_Y]} seconds";console.print(Panel(f"Running all available bridges continuously...\nPress Ctrl+C to stop\n\n{B}",title=f"{STATUS_ICONS[_O]} All Bridges Mode",border_style=_D))
		try:
			I=0
			while _M:
				if A.trial_info:A.check_trial_expiry()
				I+=1;console.print(f"[bold cyan]{STATUS_ICONS[_N]} Starting cycle {I}[/bold cyan]");J=[A for(A,B)in A.bridge_manager.get_available_bridges()]
				if not J:console.print(f"[bold red]{STATUS_ICONS[_G]} No bridges with valid data available[/bold red]");return
				D=Table(title=f"Cycle {I} Progress",box=ROUNDED,border_style=_D);D.add_column(_o,style=_D);D.add_column(_A2,style=_D);D.add_column(_A3,style=_B)
				for C in J:
					E,K=A.bridge_manager.bridge_paths[C];M,T=CHAIN_STYLES.get(E,(_B,_J));N,U=CHAIN_STYLES.get(K,(_B,_J));V=f"[{M}]{T} {E}[/{M}] → [{N}]{U} {K}[/{N}]";console.print(f"[cyan]{STATUS_ICONS[_O]} Processing bridge: {C} ({E} to {K})[/cyan]")
					for(F,W)in enumerate(A.accounts):
						O=A.labels[F]if F<len(A.labels)else f"Account {F+1}";L=_A
						if hasattr(A,_F)and _I in A.custom_delays:L=A.custom_delays[_I].get(E)
						if L is not _A:console.print(f"[cyan]{STATUS_ICONS[_L]} Using custom transaction delay for {E}: {L}s[/cyan]")
						console.print(f"[cyan]{STATUS_ICONS[_b]} Processing account: {O}[/cyan]");X,Z=A.bridge_manager.execute_bridge(C,W,A.bridge_amount)
						if X:P=f"[green]{STATUS_ICONS[_K]} Success - {A.bridge_amount} ETH[/green]"
						else:P=f"[red]{STATUS_ICONS[_G]} Failed[/red]"
						D.add_row(V,O,P);Q=A.delays[_W]
						if F<len(A.accounts)-1:console.print(f"[cyan]{STATUS_ICONS[_L]} Waiting {Q} seconds before next account...[/cyan]");time.sleep(Q)
					if C!=J[-1]:
						G=A.delays[_X]
						if hasattr(A,_F)and _C in A.custom_delays:G=A.custom_delays[_C].get(C,G)
						console.print(f"[cyan]{STATUS_ICONS[_L]} Waiting {G} seconds before next bridge...[/cyan]");time.sleep(G)
				console.print(D);R=A.delays[_Y];console.print(f"[bold cyan]{STATUS_ICONS[_L]} Completed full cycle. Waiting {R} seconds before starting again...[/bold cyan]");time.sleep(R)
		except KeyboardInterrupt:console.print(f"[yellow]{STATUS_ICONS[_H]} Stopped by user[/yellow]")
		except TrialExpiredException:console.print(f"[bold red]{STATUS_ICONS[_G]} Trial period has expired[/bold red]");time.sleep(3);return
	def check_trial_expiry(A):
		'Check if trial period has expired and raise exception if it has'
		if not A.trial_info:return
		B=pytz.timezone(_v);C=datetime.now(B).replace(tzinfo=_A);D=A.trial_info[_A1].replace(tzinfo=_A)
		if C>D:raise TrialExpiredException('Trial period has expired')
	def run(A):
		'Main UI loop'
		while _M:
			try:
				if A.trial_info:A.check_trial_expiry()
				A.clear_screen()
				try:
					B=A.display_main_menu()
					if B=='Q':break
					elif B=='RUN_ALL':A.run_all_bridges()
					elif B=='CUSTOM':A.run_custom_bridge_selection()
					elif B==_AI:A.set_bridge_amount()
					elif B==_AJ:A.set_delay_settings()
					elif B in A.bridge_manager.bridge_paths:A.run_single_bridge(B)
					else:console.print(f"[bold red]{STATUS_ICONS[_G]} Invalid choice[/bold red]");time.sleep(2)
				except KeyboardInterrupt:console.print('\n[yellow]Operation interrupted by user. Returning to main menu...[/yellow]');time.sleep(2);continue
				except Exception as C:logger.error(f"Error in UI loop: {C}");console.print(f"[bold red]{STATUS_ICONS[_G]} Error: {C}[/bold red]");console.print(f"[cyan]{STATUS_ICONS[_N]} Waiting 5 seconds before continuing...[/cyan]");time.sleep(5)
			except TrialExpiredException:A.clear_screen();console.print(Panel(f"[bold red]Your trial period has expired.[/bold red]\n\nContact the developer at https://t.me/yoakeid to get full access.",title=f"{STATUS_ICONS[_c]} Trial Expired",border_style=_i));time.sleep(5);break
class TrialExpiredException(Exception):'Exception raised when trial period has expired'
def main():
	'Main entry point for the application'
	try:
		os.system('cls'if os.name=='nt'else'clear');A=get_user_ip();M,D,H=check_ip_access(A);I=_A
		if M:console.print(Panel(f"[bold green]Your IP: {A}[/bold green]\nAccess: [bold green]Full Access[/bold green]\nValid until: [bold green]{D.strftime(_k)}[/bold green]",title=f"{STATUS_ICONS[_c]} IP Verification",border_style=_B))
		elif'trial'in H.lower():I={'ip':A,_A1:D};console.print(Panel(f"[bold yellow]Your IP: {A}[/bold yellow]\nAccess: [bold yellow]1-Hour Trial[/bold yellow]\nExpires: [bold yellow]{D.strftime(_AH)} WIB[/bold yellow]\n\nContact: https://t.me/yoakeid for full access",title=f"{STATUS_ICONS[_c]} Trial Access Granted",border_style=_p))
		else:console.print(Panel(f"[bold red]Your IP: {A}[/bold red]\nAccess: [bold red]Denied[/bold red]\n{H}\n\nContact: https://t.me/yoakeid to get access",title=f"{STATUS_ICONS[_c]} IP Verification Failed",border_style=_i));time.sleep(5);return
		time.sleep(2);N='\n                        🌉 T3RN BRIDGE BOT 🌉\n                              By Yoake\n                         https://t.me/yoakeid\n                    Smart, Fast, Reliable Bridging\n        ';console.print(Panel(N,title='Welcome!',border_style=_D,padding=(1,2)));console.print(Panel('         https://bridge.t2rn.io/ or https://unlock3d.t3rn.io/',title='Bridge URL',border_style=_h));F=[_A];B=threading.Event();C=[_A];time.sleep(3)
		def O():
			M='label';J='address'
			try:
				D=load_config();G=NetworkManager(D);K=TransactionManager(G);N=BridgeManager(D,G,K);E=[];L=[]
				for A in D['accounts']:
					try:
						O=A['private_key'];H=Account.from_key(O);E.append(H)
						if J in A and H.address.lower()!=A[J].lower():print(f"Warning: Address mismatch for {A[M]}. Expected {A[J]}, got {H.address}")
						L.append(A.get(M,f"Account {len(E)}"))
					except Exception as I:print(f"Error creating account: {I}")
				if not E:C[0]='No valid accounts found. Please update your config.json file with valid private keys.';B.set();return
				F[0]=D,G,K,N,E,L
			except Exception as I:C[0]=str(I)
			finally:B.set()
		print('Initializing T3RN Bridge Bot...');E=threading.Thread(target=O);E.daemon=_M;E.start();P=30;J=time.time();K=['|','/','-','\\'];G=0
		while not B.is_set()and time.time()-J<P:print(f"\rInitializing... {K[G]} ({int(time.time()-J)}s)",end='');G=(G+1)%len(K);time.sleep(.2)
		print('\r'+' '*50+'\r',end='')
		if not B.is_set():print('Initialization timed out! Continuing with limited functionality.');E.join(.1)
		if C[0]:print(f"Error during initialization: {C[0]}");return
		if not F[0]:print('Failed to initialize application components.');return
		Q,R,S,T,U,V=F[0];W=UserInterface(Q,R,S,T,U,V,I);W.run()
	except KeyboardInterrupt:print('\nApplication terminated by user.')
	except Exception as L:logger.error(f"Unexpected error: {L}");print(f"Unexpected error: {L}");print('Please check the log file for details.')
if __name__=='__main__':main()
