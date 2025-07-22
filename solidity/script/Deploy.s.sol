// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.19;

import "@forge-std/Script.sol";
import "../src/contracts/AgentRegistrySimple.sol";
import "../src/contracts/MessagingSimple.sol";

/**
 * @title Deploy
 * @notice Deployment script for PostFiat SDK contracts
 * @dev Run with: forge script script/Deploy.s.sol --rpc-url <RPC_URL> --broadcast
 */
contract Deploy is Script {
    function run() external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        
        vm.startBroadcast(deployerPrivateKey);
        
        // Deploy AgentRegistry
        AgentRegistrySimple agentRegistry = new AgentRegistrySimple();
        console.log("AgentRegistrySimple deployed at:", address(agentRegistry));
        
        // Deploy Messaging
        MessagingSimple messaging = new MessagingSimple();
        console.log("MessagingSimple deployed at:", address(messaging));
        
        // Optional: Set up integration between contracts
        messaging.setAgentRegistry(address(agentRegistry));
        console.log("Agent registry integration configured");
        
        vm.stopBroadcast();
        
        // Log deployment summary
        console.log("\n=== PostFiat SDK Deployment Summary ===");
        console.log("AgentRegistry:", address(agentRegistry));
        console.log("Messaging:", address(messaging));
        console.log("Network:", block.chainid);
        console.log("Block:", block.number);
    }
}