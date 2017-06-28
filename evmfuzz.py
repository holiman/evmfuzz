import random
import string
import subprocess

G_VM = "/home/martin/go/src/github.com/ethereum/go-ethereum/build/bin/evm"
P_VM = "/home/martin/workspace/parity/target/release/parity-evm"

def cmdGeth(genesis = None, code = "", gas = 0):
	"""evm --debug --gas 1048575 --code ""  --json run  
	"""
	cmd = [G_VM, "--code", code ,"--json"]
	if gas > 0: 
		cmd.append("--gas")
		cmd.append("%d" % gas)
	cmd.append("run")

	return cmd


def cmdParity(genesis = None, code = "", gas = 0):
	"""parity-evm --code 732a50613a76a4c2c58d052d5ebf3b03ed3227eae9316001600155  --json --gas fffff
	"""
	cmd = [P_VM, "--code", code , "--json"]
	if gas > 0: 
		cmd.append("--gas")
		cmd.append("%s" % hex(gas)[2:])

	return cmd

def outputs(stdouts):
	import json
	finished = False
	while not finished:
		items = []
		for stdout in stdouts:	
			outp = stdout.readline()
			if outp == "":
				items.append({})
				finished = True
			else:
				outp = outp.strip()
				try:
					items.append(json.loads(outp))
				except ValueError:
					print("Invalid json: %s" % outp)
					items.append({})
		yield items

def canon(str):
	if str in [None, "0x", ""]:
		return ""
	if str[:2] == "0x":
		return str
	return "0x" + str

def toText(op):
	if len(op.keys()) == 0:
		return "END"
	if 'pc' in op.keys():
		return "pc {pc} op {op} gas {gas} cost {gasCost} depth {depth} stack {stack}".format(**op)
	elif 'output' in op.keys():
		op['output'] = canon(op['output'])
		return "output {output} gasUsed {gasUsed}".format(**op)
	return "N/A"

def execute(code, gas = 0xFFFF, verbose = False):
	import subprocess

	cmd_g = cmdGeth(code = code, gas = gas)
	cmd_p = cmdParity(code = code, gas = gas)

	if verbose: 
		print("Call info")
		print " ".join(cmd_g)
		print " ".join(cmd_p)
		print ""

	geth_p = subprocess.Popen(cmd_g, shell=False, stdout=subprocess.PIPE, close_fds=True)
	parity_p = subprocess.Popen(cmd_p, shell=False, stdout=subprocess.PIPE, close_fds=True)
	outp1 = geth_p.stdout
	outp2 = parity_p.stdout


	for items in outputs([outp1, outp2]):
		[g,p] = items

		a = toText(g)
		b = toText(p)

		if a == b:
			print "[*] %s" % a
		else:
			print("[!!] G:>> %s \n\t(%s)" % (a, g))
			print("[!!] P:>> %s \n\t(%s)" % (b, p))


	return


def fuzz(gas):

	for i in range(1,10):
		print("----Fuzzing--- ")
		code = ''.join(random.choice(string.hexdigits) for _ in range(100))
		execute(code, gas )
		print("-------- ")


def main():
	# parse args
	code = "732a50613a76a4c2c58d052d5ebf3b03ed3227eae9316001600155"
	gas = 0xffff

	execute(code, gas)
	fuzz(gas )



if __name__ == '__main__':
	main()





