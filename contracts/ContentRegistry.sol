// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract ContentRegistry {
    struct Record { bytes32 fingerprint; uint256 timestamp; address submitter; }
    mapping(bytes32 => Record) public records;
    event ContentRegistered(bytes32 indexed fingerprint, uint256 timestamp, address indexed submitter);

    function registerContent(bytes32 fingerprint) external {
        require(records[fingerprint].timestamp == 0, "fingerprint already registered");
        records[fingerprint] = Record(fingerprint, block.timestamp, msg.sender);
        emit ContentRegistered(fingerprint, block.timestamp, msg.sender);
    }

    function verifyContent(bytes32 fingerprint) external view returns (bool exists, uint256 timestamp, address submitter) {
        Record memory record = records[fingerprint];
        return (record.timestamp != 0, record.timestamp, record.submitter);
    }
}
