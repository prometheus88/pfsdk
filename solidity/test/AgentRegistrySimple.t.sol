// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.19;

import "@forge-std/Test.sol";
import "../src/contracts/AgentRegistrySimple.sol";

contract AgentRegistrySimpleTest is Test {
    AgentRegistrySimple public registry;
    
    address public alice = address(0x1);
    address public bob = address(0x2);
    
    string public constant AGENT_ID = "test-agent-123";
    string public constant PUBLIC_KEY = "1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2";
    string public constant METADATA_URI = "ipfs://QmTest123";
    
    function setUp() public {
        registry = new AgentRegistrySimple();
    }
    
    function testRegisterAgent() public {
        vm.prank(alice);
        registry.registerAgent(AGENT_ID, PUBLIC_KEY, METADATA_URI);
        
        AgentRegistrySimple.AgentInfo memory agent = registry.getAgent(AGENT_ID);
        
        assertEq(agent.agentId, AGENT_ID);
        assertEq(agent.publicKeyBase58, PUBLIC_KEY);
        assertEq(agent.metadataUri, METADATA_URI);
        assertEq(agent.registrar, alice);
        assertTrue(agent.active);
        assertGt(agent.registeredAt, 0);
    }
    
    function testCannotRegisterDuplicateAgent() public {
        vm.prank(alice);
        registry.registerAgent(AGENT_ID, PUBLIC_KEY, METADATA_URI);
        
        vm.prank(bob);
        vm.expectRevert(AgentRegistrySimple.AgentAlreadyExists.selector);
        registry.registerAgent(AGENT_ID, "different-key", "different-uri");
    }
    
    function testUpdateAgent() public {
        vm.prank(alice);
        registry.registerAgent(AGENT_ID, PUBLIC_KEY, METADATA_URI);
        
        string memory newKey = "new-public-key";
        string memory newUri = "ipfs://QmNewTest";
        
        vm.prank(alice);
        registry.updateAgent(AGENT_ID, newKey, newUri);
        
        AgentRegistrySimple.AgentInfo memory agent = registry.getAgent(AGENT_ID);
        assertEq(agent.publicKeyBase58, newKey);
        assertEq(agent.metadataUri, newUri);
    }
    
    function testCannotUpdateUnownedAgent() public {
        vm.prank(alice);
        registry.registerAgent(AGENT_ID, PUBLIC_KEY, METADATA_URI);
        
        vm.prank(bob);
        vm.expectRevert(AgentRegistrySimple.UnauthorizedUpdate.selector);
        registry.updateAgent(AGENT_ID, "new-key", "new-uri");
    }
    
    function testDeactivateAgent() public {
        vm.prank(alice);
        registry.registerAgent(AGENT_ID, PUBLIC_KEY, METADATA_URI);
        
        vm.prank(alice);
        registry.deactivateAgent(AGENT_ID);
        
        AgentRegistrySimple.AgentInfo memory agent = registry.getAgent(AGENT_ID);
        assertFalse(agent.active);
    }
    
    function testGetAgentStatus() public {
        (bool exists, bool active) = registry.getAgentStatus(AGENT_ID);
        assertFalse(exists);
        assertFalse(active);
        
        vm.prank(alice);
        registry.registerAgent(AGENT_ID, PUBLIC_KEY, METADATA_URI);
        
        (exists, active) = registry.getAgentStatus(AGENT_ID);
        assertTrue(exists);
        assertTrue(active);
        
        vm.prank(alice);
        registry.deactivateAgent(AGENT_ID);
        
        (exists, active) = registry.getAgentStatus(AGENT_ID);
        assertTrue(exists);
        assertFalse(active);
    }
    
    function testGetAgentsByRegistrar() public {
        vm.startPrank(alice);
        registry.registerAgent("agent-1", PUBLIC_KEY, METADATA_URI);
        registry.registerAgent("agent-2", PUBLIC_KEY, METADATA_URI);
        vm.stopPrank();
        
        vm.prank(bob);
        registry.registerAgent("agent-3", PUBLIC_KEY, METADATA_URI);
        
        string[] memory aliceAgents = registry.getAgentsByRegistrar(alice);
        assertEq(aliceAgents.length, 2);
        assertEq(aliceAgents[0], "agent-1");
        assertEq(aliceAgents[1], "agent-2");
        
        string[] memory bobAgents = registry.getAgentsByRegistrar(bob);
        assertEq(bobAgents.length, 1);
        assertEq(bobAgents[0], "agent-3");
    }
    
    function testGetAgentIds() public {
        vm.startPrank(alice);
        registry.registerAgent("agent-1", PUBLIC_KEY, METADATA_URI);
        registry.registerAgent("agent-2", PUBLIC_KEY, METADATA_URI);
        registry.registerAgent("agent-3", PUBLIC_KEY, METADATA_URI);
        vm.stopPrank();
        
        assertEq(registry.getTotalAgents(), 3);
        
        string[] memory page1 = registry.getAgentIds(0, 2);
        assertEq(page1.length, 2);
        assertEq(page1[0], "agent-1");
        assertEq(page1[1], "agent-2");
        
        string[] memory page2 = registry.getAgentIds(2, 2);
        assertEq(page2.length, 1);
        assertEq(page2[0], "agent-3");
        
        string[] memory emptyPage = registry.getAgentIds(10, 2);
        assertEq(emptyPage.length, 0);
    }
    
    function testInvalidInputs() public {
        vm.expectRevert(AgentRegistrySimple.InvalidInput.selector);
        registry.registerAgent("", PUBLIC_KEY, METADATA_URI);
        
        vm.expectRevert(AgentRegistrySimple.InvalidInput.selector);
        registry.registerAgent(AGENT_ID, "", METADATA_URI);
    }
    
    function testGetNonexistentAgent() public {
        vm.expectRevert(AgentRegistrySimple.AgentNotFound.selector);
        registry.getAgent("nonexistent");
    }
}