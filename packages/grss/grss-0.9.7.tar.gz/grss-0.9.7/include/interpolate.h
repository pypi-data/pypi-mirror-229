#ifndef INTERPOLATE_H
#define INTERPOLATE_H

#include "force.h"
#include "gr15.h"

void interpolate_on_the_fly(propSimulation *propSim, const real &t, const real &dt);
void interpolate(const real &t, const real &dt,
                 const std::vector<real> &xInteg0,
                 const std::vector<real> &accInteg0,
                 const std::vector<std::vector<real>> &b,
                 propSimulation *propSim);
void get_coeffs(const std::vector<real> &tVecForInterp,
                const std::vector<std::vector<real>> &xIntegForInterp,
                std::vector<std::vector<real>> &coeffs);
void evaluate_one_interpolation(const propSimulation *propSim, const real &t,
                                const real &dt, const real &tInterp,
                                std::vector<real> &xInterp);
void evaluate_one_interpolation(
    const propSimulation *propSim, const real &tInterp,
    const std::vector<real> &tVecForInterp,
    const std::vector<std::vector<real>> &coeffs,
    const std::vector<real> &tVecForInterpPrev,
    const std::vector<std::vector<real>> &coeffsPrev,
    std::vector<real> &xInterp);
void get_interpIdxInWindow(const propSimulation *propSim,
                           const real &tWindowStart, const real &tNext,
                           const bool &forwardIntegrate,
                           const bool &backwardIntegrate,
                           bool &interpIdxInWindow);
void one_timestep_interpolation(
    const real &tNext, const std::vector<real> &tVecForInterp,
    const std::vector<std::vector<real>> &xIntegForInterp,
    std::vector<real> &tVecForInterpPrev,
    std::vector<std::vector<real>> &xIntegForInterpPrev,
    propSimulation *propSim);
void get_lightTime_and_xRelative(propSimulation *propSim,
                                 const size_t interpIdx, const real &t,
                                 const real &dt, const real tInterpGeom,
                                 const std::vector<real> &xInterpGeom,
                                 std::vector<real> &lightTime,
                                 std::vector<real> &xInterpApparent);
void get_lightTime_and_xRelative(
    const size_t interpIdx, const real tInterpGeom,
    const std::vector<real> &xInterpGeom,
    const std::vector<real> &tVecForInterp,
    const std::vector<std::vector<real>> &coeffs,
    const std::vector<real> &tVecForInterpPrev,
    const std::vector<std::vector<real>> &coeffsPrev, propSimulation *propSim,
    std::vector<real> &lightTime, std::vector<real> &xInterpApparent);
void get_lightTimeOneBody(propSimulation *propSim, const size_t &i,
                          const real tInterpGeom, std::vector<real> xInterpGeom,
                          std::vector<real> xObserver,
                          const bool bouncePointAtLeadingEdge, const real &t,
                          const real &dt, real &lightTimeOneBody);
void get_lightTimeOneBody(const size_t &i, const real tInterpGeom,
                          std::vector<real> xInterpGeom,
                          std::vector<real> xObserver,
                          const bool bouncePointAtLeadingEdge,
                          const std::vector<real> &tVecForInterp,
                          const std::vector<std::vector<real>> &coeffs,
                          const std::vector<real> &tVecForInterpPrev,
                          const std::vector<std::vector<real>> &coeffsPrev,
                          propSimulation *propSim, real &lightTimeOneBody);
void get_glb_correction(propSimulation *propSim, const real &tInterpGeom,
                        std::vector<real> &xInterpApparentBary);
void get_radar_measurement(propSimulation *propSim, const size_t interpIdx,
                           const real &t, const real &dt,
                           const real tInterpGeom,
                           const std::vector<real> &xInterpGeom,
                           std::vector<real> &radarMeasurement);
void get_radar_measurement(const size_t interpIdx, const real tInterpGeom,
                           const std::vector<real> &xInterpGeom,
                           const std::vector<real> &tVecForInterp,
                           const std::vector<std::vector<real>> &coeffs,
                           const std::vector<real> &tVecForInterpPrev,
                           const std::vector<std::vector<real>> &coeffsPrev,
                           propSimulation *propSim,
                           std::vector<real> &radarMeasurement);
void get_delta_delay_relativistic(propSimulation *propSim,
                                  const real &tForSpice,
                                  const std::vector<real> &targetState,
                                  const Constants &consts,
                                  real &deltaDelayRelativistic);
void get_doppler_measurement(propSimulation *propSim, const real receiveTimeTDB,
                             const real transmitTimeTDB,
                             const std::vector<real> xObsBaryRcv,
                             const std::vector<real> xTrgtBaryBounce,
                             const std::vector<real> xObsBaryTx,
                             const real transmitFreq, real &dopplerMeasurement);

#endif
