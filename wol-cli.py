#!/usr/bin/python3
import socket
import json
import os

MAC_FILE = "saved_macs.json"

try:
    if os.path.exists(MAC_FILE):
        with open(MAC_FILE, "r") as f:
            saved_macs = json.load(f)
    else:
        saved_macs = {}

    print("已保存的 MAC 列表：")
    if saved_macs:
        for i, name in enumerate(saved_macs, 1):
            print(f"{i}. {name}: {saved_macs[name]}")
    else:
        print("（暂无已保存的 MAC）")
    print("n. 新增 MAC")

    choice = input("选择编号或输入 n 新增 MAC：").strip()

    if choice.lower() == 'n':
        name = input("为这个 MAC 命名：").strip()
        MAC = input("输入 MAC 地址（格式 00:E0:21:09:30:1C）：").strip()
        saved_macs[name] = MAC
        with open(MAC_FILE, "w") as f:
            json.dump(saved_macs, f, indent=2)
    else:
        index = int(choice) - 1
        name = list(saved_macs.keys())[index]
        MAC = saved_macs[name]
        print(f"已选择 {name}: {MAC}")

    mac_bytes = bytes.fromhex(MAC.replace(":", "").replace("-", ""))
    packet = b'\xff' * 6 + mac_bytes * 16

    print("请选择WOL模式：")
    print("1. LAN模式（直接通过物理网卡广播）")
    print("2. ROUTER模式（通过UDP广播跨路由器）")
    choice = input("输入选项(1或2)：").strip()

    if choice == "1":
        def get_physical_and_vpn_interfaces():
            interfaces = []
            for iface in os.listdir("/sys/class/net/"):
                if iface == "lo":
                    continue
                if os.path.exists(f"/sys/class/net/{iface}/device"):
                    interfaces.append(iface)
                elif any(iface.startswith(prefix) for prefix in (
                        "tun", "tap", "wg", "tailscale", "ppp", "vpn")):
                    interfaces.append(iface)
            return interfaces

        interfaces = get_physical_and_vpn_interfaces()
        if not interfaces:
            print("未检测到可用网卡！")
            exit()

        print("请选择发送网卡：")
        for i, iface in enumerate(interfaces):
            print(f"{i+1}. {iface}")
        iface_choice = int(input("输入网卡编号：").strip()) - 1
        IFACE = interfaces[iface_choice]

        dest_mac = b'\xff\xff\xff\xff\xff\xff'
        eth_type = b'\x08\x42'
        frame = dest_mac + b'\x00\x00\x00\x00\x00\x00' + eth_type + packet

        sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
        sock.bind((IFACE, 0))
        sock.send(frame)
        sock.close()
        print(f"Magic Packet sent to {MAC} via {IFACE} (LAN模式)")

    elif choice == "2":
        GATEWAY_IP = "255.255.255.255"
        UDP_PORT = 9

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(packet, (GATEWAY_IP, UDP_PORT))
        sock.close()
        print(f"Magic Packet sent to {MAC} via UDP broadcast (ROUTER模式)")

    else:
        print("无效选项，退出")

except KeyboardInterrupt:
    print("\n用户中断，退出脚本。")
    exit()
except Exception as e:
    print(f"\n发生错误: {e}")
    exit()
