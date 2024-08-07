# standard python imports
import math
import typing

# project imports
from robot import MyRobot
import subsystems.drive.constants
from utils.units import unit

# wpi imports
from wpilib import DriverStation, RobotController, SmartDashboard
import wpilib.simulation as sim
from wpimath.system.plant import DCMotor
from pyfrc.physics.core import PhysicsInterface
from pyfrc.physics import drivetrains

# vendor imports
from  phoenix6.sim import ChassisReference
from phoenix6 import unmanaged

class PhysicsEngine:
    """
    Simulates a swerve robot
    """

    def __init__(self, physics_controller: PhysicsInterface, robot: "MyRobot"):
        """
        :param physics_controller: `pyfrc.physics.core.Physics` object
                                   to communicate simulation effects to
        :param robot: your robot object
        """

        self.physics_controller = physics_controller
        self.robot = robot
        self.drivetrain = robot.container.robotDrive

        self.drive_ratio = subsystems.drive.constants.kDriveRatio
        self.turn_ratio = subsystems.drive.constants.kTurnRatio

        backLeftTurn = sim.DCMotorSim(DCMotor.krakenX60(1), self.turn_ratio, 0.01)
        backLeftTurn.setState(0,0)
        self.drivetrain.backLeft.turningMotor.sim_state.set_raw_rotor_position(0)
        backRightTurn = sim.DCMotorSim(DCMotor.krakenX60(1), self.turn_ratio, 0.01)
        backRightTurn.setState(0,0)
        self.drivetrain.backRight.turningMotor.sim_state.set_raw_rotor_position(0)
        frontLeftTurn = sim.DCMotorSim(DCMotor.krakenX60(1), self.turn_ratio, 0.01)
        frontLeftTurn.setState(0,0)
        self.drivetrain.frontLeft.turningMotor.sim_state.set_raw_rotor_position(0)
        frontRightTurn = sim.DCMotorSim(DCMotor.krakenX60(1), self.turn_ratio, 0.01)
        frontRightTurn.setState(0,0)
        self.drivetrain.frontRight.turningMotor.sim_state.set_raw_rotor_position(0)
        
        
        self.swerve_sim_devices = [[self.drivetrain.backLeft.driveMotor.sim_state, sim.DCMotorSim(DCMotor.krakenX60(1), self.drive_ratio, 0.01), self.drivetrain.backLeft.turningMotor.sim_state, backLeftTurn, self.drivetrain.backLeft.turningEncoder.sim_state],
                              [self.drivetrain.backRight.driveMotor.sim_state, sim.DCMotorSim(DCMotor.krakenX60(1), self.drive_ratio, 0.01), self.drivetrain.backRight.turningMotor.sim_state, backRightTurn, self.drivetrain.backRight.turningEncoder.sim_state],
                              [self.drivetrain.frontLeft.driveMotor.sim_state, sim.DCMotorSim(DCMotor.krakenX60(1), self.drive_ratio, 0.01), self.drivetrain.frontLeft.turningMotor.sim_state, frontLeftTurn, self.drivetrain.frontLeft.turningEncoder.sim_state],
                              [self.drivetrain.frontRight.driveMotor.sim_state, sim.DCMotorSim(DCMotor.krakenX60(1), self.drive_ratio, 0.01), self.drivetrain.frontRight.turningMotor.sim_state, frontRightTurn, self.drivetrain.frontRight.turningEncoder.sim_state]]

        self.drivetrain.backLeft.turningMotor.sim_state.orientation = ChassisReference.Clockwise_Positive
        self.drivetrain.backRight.turningMotor.sim_state.orientation = ChassisReference.Clockwise_Positive
        self.drivetrain.frontLeft.turningMotor.sim_state.orientation = ChassisReference.Clockwise_Positive
        self.drivetrain.frontRight.turningMotor.sim_state.orientation = ChassisReference.Clockwise_Positive

        self.drivetrain.backLeft.turningEncoder.sim_state.orientation = ChassisReference.CounterClockwise_Positive
        self.drivetrain.backRight.turningEncoder.sim_state.orientation = ChassisReference.CounterClockwise_Positive
        self.drivetrain.frontLeft.turningEncoder.sim_state.orientation = ChassisReference.CounterClockwise_Positive
        self.drivetrain.frontRight.turningEncoder.sim_state.orientation = ChassisReference.CounterClockwise_Positive

    def update_sim(self, now: float, tm_diff: float) -> None:
        """
        Called when the simulation parameters for the program need to be
        updated.

        :param now: The current time as a float
        :param tm_diff: The amount of time that has passed since the last
                        time that this function was called
        """

        if DriverStation.isEnabled():
            unmanaged.feed_enable(100)

        for corner in self.swerve_sim_devices:
            drive_fx, drive_motor, turn_fx, turn_motor, turn_encoder = corner

            drive_fx.set_supply_voltage(RobotController.getBatteryVoltage())
            drive_motor.setInputVoltage(drive_fx.motor_voltage)
            drive_motor.update(tm_diff)
            drive_fx.set_raw_rotor_position((drive_motor.getAngularPosition() * self.drive_ratio * unit.radian).m_as("turn"))
            drive_fx.set_rotor_velocity((drive_motor.getAngularVelocity() * self.drive_ratio * unit.radian / unit.second).m_as("turn / second"))

            turn_fx.set_supply_voltage(RobotController.getBatteryVoltage())
            turn_motor.setInputVoltage(turn_fx.motor_voltage)
            turn_motor.update(tm_diff)
            turn_encoder.set_raw_position((turn_motor.getAngularPosition() * unit.radian).m_as("turn"))
            turn_encoder.set_velocity((turn_motor.getAngularVelocity() * unit.radian / unit.second).m_as("turn / second"))
            turn_fx.set_raw_rotor_position((turn_motor.getAngularPosition() * self.turn_ratio * unit.radian).m_as("turn"))
            turn_fx.set_rotor_velocity((turn_motor.getAngularVelocity() * self.turn_ratio * unit.radian / unit.second).m_as("turn / second"))

        # speeds = \
        # drivetrains.four_motor_swerve_drivetrain(self.swerve_sim_devices[1][0].motor_voltage/RobotController.getBatteryVoltage(),
        #                                          self.swerve_sim_devices[2][0].motor_voltage/RobotController.getBatteryVoltage(),
        #                                          self.swerve_sim_devices[3][0].motor_voltage/RobotController.getBatteryVoltage(),
        #                                          self.swerve_sim_devices[0][0].motor_voltage/RobotController.getBatteryVoltage(),
        #                                          360 - ((self.swerve_sim_devices[1][3].getAngularPosition()) * unit.radian).m_as("degree"),
        #                                          360 - ((self.swerve_sim_devices[2][3].getAngularPosition()) * unit.radian).m_as("degree"),
        #                                          360 - ((self.swerve_sim_devices[3][3].getAngularPosition()) * unit.radian).m_as("degree"),
        #                                          360 - ((self.swerve_sim_devices[0][3].getAngularPosition()) * unit.radian).m_as("degree"),
        #                                          subsystems.drive.constants.kChassisWidth.m_as("feet"),
        #                                          subsystems.drive.constants.kChassisLength.m_as("feet"),
        #                                          subsystems.drive.constants.kMaxSpeed.m_as("feet / second")
        #                                          )
        
        self.drivetrain.gyro.sim_state.set_supply_voltage(RobotController.getBatteryVoltage())