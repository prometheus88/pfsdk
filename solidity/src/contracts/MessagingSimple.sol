// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.19;

/**
 * @title MessagingSimple
 * @notice Simplified on-chain messaging system for PostFiat agents
 * @dev Basic version without protobuf integration for getting started
 */
contract MessagingSimple {
    struct Message {
        string envelopeId;
        address sender;
        string recipient;
        string contentUri;
        uint256 timestamp;
        uint256 blockNumber;
        MessageStatus status;
    }
    
    enum MessageStatus {
        SENT,
        ACKNOWLEDGED,
        FAILED
    }
    
    // Events
    event MessageSent(
        string indexed envelopeId,
        address indexed sender,
        string indexed recipient,
        string contentUri,
        uint256 timestamp
    );
    
    event MessageAcknowledged(
        string indexed envelopeId,
        string indexed recipient,
        uint256 timestamp
    );
    
    event MessageFailed(
        string indexed envelopeId,
        string indexed recipient,
        string reason,
        uint256 timestamp
    );
    
    // Errors
    error MessageNotFound();
    error MessageAlreadyExists();
    error InvalidStatus();
    error UnauthorizedOperation();
    error InvalidInput();
    
    // State
    mapping(string => Message) public messages;
    mapping(string => string[]) public recipientMessages;
    mapping(address => string[]) public senderMessages;
    
    // Optional: Agent registry integration
    address public agentRegistry;
    
    modifier validEnvelopeId(string memory envelopeId) {
        if (bytes(envelopeId).length == 0) {
            revert InvalidInput();
        }
        _;
    }
    
    modifier messageExists(string memory envelopeId) {
        if (messages[envelopeId].timestamp == 0) {
            revert MessageNotFound();
        }
        _;
    }
    
    /**
     * @notice Set the agent registry contract address
     * @param _agentRegistry Address of the agent registry
     */
    function setAgentRegistry(address _agentRegistry) external {
        // In a production system, you'd want proper access control here
        agentRegistry = _agentRegistry;
    }
    
    /**
     * @notice Send a message to a recipient
     * @param envelopeId Unique envelope identifier
     * @param recipient Recipient agent ID
     * @param contentUri URI to message content (IPFS, HTTP, etc.)
     */
    function sendMessage(
        string memory envelopeId,
        string memory recipient,
        string memory contentUri
    ) external validEnvelopeId(envelopeId) {
        if (bytes(recipient).length == 0) {
            revert InvalidInput();
        }
        
        if (messages[envelopeId].timestamp != 0) {
            revert MessageAlreadyExists();
        }
        
        messages[envelopeId] = Message({
            envelopeId: envelopeId,
            sender: msg.sender,
            recipient: recipient,
            contentUri: contentUri,
            timestamp: block.timestamp,
            blockNumber: block.number,
            status: MessageStatus.SENT
        });
        
        recipientMessages[recipient].push(envelopeId);
        senderMessages[msg.sender].push(envelopeId);
        
        emit MessageSent(
            envelopeId,
            msg.sender,
            recipient,
            contentUri,
            block.timestamp
        );
    }
    
    /**
     * @notice Acknowledge receipt of a message
     * @param envelopeId Envelope identifier
     */
    function acknowledgeMessage(string memory envelopeId) 
        external 
        messageExists(envelopeId) 
    {
        Message storage message = messages[envelopeId];
        
        if (message.status != MessageStatus.SENT) {
            revert InvalidStatus();
        }
        
        // In a more sophisticated system, you might want to verify
        // that msg.sender is authorized to acknowledge on behalf of recipient
        
        message.status = MessageStatus.ACKNOWLEDGED;
        
        emit MessageAcknowledged(
            envelopeId,
            message.recipient,
            block.timestamp
        );
    }
    
    /**
     * @notice Mark a message as failed
     * @param envelopeId Envelope identifier
     * @param reason Failure reason
     */
    function markMessageFailed(string memory envelopeId, string memory reason) 
        external 
        messageExists(envelopeId) 
    {
        Message storage message = messages[envelopeId];
        
        if (message.status != MessageStatus.SENT) {
            revert InvalidStatus();
        }
        
        // Only sender can mark their own message as failed
        if (message.sender != msg.sender) {
            revert UnauthorizedOperation();
        }
        
        message.status = MessageStatus.FAILED;
        
        emit MessageFailed(
            envelopeId,
            message.recipient,
            reason,
            block.timestamp
        );
    }
    
    /**
     * @notice Get messages for a recipient
     * @param recipient Recipient agent ID
     * @return messageIds Array of envelope IDs
     */
    function getMessagesForRecipient(string memory recipient) 
        external 
        view 
        returns (string[] memory) 
    {
        return recipientMessages[recipient];
    }
    
    /**
     * @notice Get messages sent by an address
     * @param sender Sender address
     * @return messageIds Array of envelope IDs
     */
    function getMessagesFromSender(address sender) 
        external 
        view 
        returns (string[] memory) 
    {
        return senderMessages[sender];
    }
    
    /**
     * @notice Get message details
     * @param envelopeId Envelope identifier
     * @return message Message struct
     */
    function getMessage(string memory envelopeId) 
        external 
        view 
        returns (Message memory) 
    {
        Message memory message = messages[envelopeId];
        if (message.timestamp == 0) {
            revert MessageNotFound();
        }
        return message;
    }
    
    /**
     * @notice Get message status
     * @param envelopeId Envelope identifier
     * @return status Current message status
     */
    function getMessageStatus(string memory envelopeId) 
        external 
        view 
        returns (MessageStatus) 
    {
        Message memory message = messages[envelopeId];
        if (message.timestamp == 0) {
            revert MessageNotFound();
        }
        return message.status;
    }
    
    /**
     * @notice Get count of messages for recipient
     * @param recipient Recipient agent ID
     * @return count Number of messages
     */
    function getRecipientMessageCount(string memory recipient) 
        external 
        view 
        returns (uint256) 
    {
        return recipientMessages[recipient].length;
    }
    
    /**
     * @notice Get count of messages from sender
     * @param sender Sender address
     * @return count Number of messages
     */
    function getSenderMessageCount(address sender) 
        external 
        view 
        returns (uint256) 
    {
        return senderMessages[sender].length;
    }
}