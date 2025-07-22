// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.19;

/**
 * @title AgentRegistrySimple
 * @notice Simplified on-chain registry for PostFiat agents
 * @dev Basic version without protobuf integration for getting started
 */
contract AgentRegistrySimple {
    struct AgentInfo {
        string agentId;
        string publicKeyBase58;
        string metadataUri;
        address registrar;
        uint256 registeredAt;
        uint256 updatedAt;
        bool active;
    }
    
    // Events
    event AgentRegistered(
        string indexed agentId,
        address indexed registrar,
        string publicKeyBase58,
        uint256 timestamp
    );
    
    event AgentUpdated(
        string indexed agentId,
        string publicKeyBase58,
        uint256 timestamp
    );
    
    event AgentDeactivated(
        string indexed agentId,
        uint256 timestamp
    );
    
    // Errors
    error AgentNotFound();
    error UnauthorizedUpdate();
    error AgentAlreadyExists();
    error InvalidInput();
    
    // Storage
    mapping(string => AgentInfo) private agents;
    mapping(address => string[]) private agentsByRegistrar;
    string[] private allAgentIds;
    
    // Modifiers
    modifier onlyAgentOwner(string memory agentId) {
        if (agents[agentId].registrar != msg.sender) {
            revert UnauthorizedUpdate();
        }
        _;
    }
    
    modifier validAgentId(string memory agentId) {
        if (bytes(agentId).length == 0) {
            revert InvalidInput();
        }
        _;
    }
    
    /**
     * @notice Register a new agent
     * @param agentId Unique agent identifier
     * @param publicKeyBase58 Base58-encoded public key
     * @param metadataUri URI pointing to agent metadata
     */
    function registerAgent(
        string memory agentId,
        string memory publicKeyBase58,
        string memory metadataUri
    ) external validAgentId(agentId) {
        if (agents[agentId].registrar != address(0)) {
            revert AgentAlreadyExists();
        }
        
        if (bytes(publicKeyBase58).length == 0) {
            revert InvalidInput();
        }
        
        agents[agentId] = AgentInfo({
            agentId: agentId,
            publicKeyBase58: publicKeyBase58,
            metadataUri: metadataUri,
            registrar: msg.sender,
            registeredAt: block.timestamp,
            updatedAt: block.timestamp,
            active: true
        });
        
        agentsByRegistrar[msg.sender].push(agentId);
        allAgentIds.push(agentId);
        
        emit AgentRegistered(
            agentId,
            msg.sender,
            publicKeyBase58,
            block.timestamp
        );
    }
    
    /**
     * @notice Update an existing agent
     * @param agentId Agent identifier
     * @param publicKeyBase58 Updated public key
     * @param metadataUri Updated metadata URI
     */
    function updateAgent(
        string memory agentId,
        string memory publicKeyBase58,
        string memory metadataUri
    ) external onlyAgentOwner(agentId) {
        if (bytes(publicKeyBase58).length == 0) {
            revert InvalidInput();
        }
        
        AgentInfo storage agent = agents[agentId];
        agent.publicKeyBase58 = publicKeyBase58;
        agent.metadataUri = metadataUri;
        agent.updatedAt = block.timestamp;
        
        emit AgentUpdated(agentId, publicKeyBase58, block.timestamp);
    }
    
    /**
     * @notice Deactivate an agent
     * @param agentId Agent identifier
     */
    function deactivateAgent(string memory agentId) external onlyAgentOwner(agentId) {
        agents[agentId].active = false;
        agents[agentId].updatedAt = block.timestamp;
        
        emit AgentDeactivated(agentId, block.timestamp);
    }
    
    /**
     * @notice Get agent information
     * @param agentId Agent identifier
     * @return agent AgentInfo struct
     */
    function getAgent(string memory agentId) external view returns (AgentInfo memory) {
        AgentInfo memory agent = agents[agentId];
        if (agent.registrar == address(0)) {
            revert AgentNotFound();
        }
        return agent;
    }
    
    /**
     * @notice Check if agent exists and is active
     * @param agentId Agent identifier
     * @return exists Whether agent exists
     * @return active Whether agent is active
     */
    function getAgentStatus(string memory agentId) external view returns (bool exists, bool active) {
        AgentInfo memory agent = agents[agentId];
        return (agent.registrar != address(0), agent.active);
    }
    
    /**
     * @notice Get all agents registered by an address
     * @param registrar Registrar address
     * @return agentIds Array of agent IDs
     */
    function getAgentsByRegistrar(address registrar) external view returns (string[] memory) {
        return agentsByRegistrar[registrar];
    }
    
    /**
     * @notice Get total number of registered agents
     * @return count Total agent count
     */
    function getTotalAgents() external view returns (uint256) {
        return allAgentIds.length;
    }
    
    /**
     * @notice Get a page of agent IDs
     * @param offset Starting index
     * @param limit Maximum number of results
     * @return agentIds Array of agent IDs
     */
    function getAgentIds(uint256 offset, uint256 limit) 
        external 
        view 
        returns (string[] memory agentIds) 
    {
        uint256 total = allAgentIds.length;
        if (offset >= total) {
            return new string[](0);
        }
        
        uint256 end = offset + limit;
        if (end > total) {
            end = total;
        }
        
        agentIds = new string[](end - offset);
        for (uint256 i = offset; i < end; i++) {
            agentIds[i - offset] = allAgentIds[i];
        }
    }
}