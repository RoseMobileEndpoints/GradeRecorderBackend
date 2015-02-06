/* This file was generated by the ServiceGenerator.
 * The ServiceGenerator is Copyright (c) 2015 Google Inc.
 */

//
//  GTLGraderecorderGradeEntry.m
//

// ----------------------------------------------------------------------------
// NOTE: This file is generated from Google APIs Discovery Service.
// Service:
//   graderecorder/v1
// Description:
//   Grade Recorder API
// Classes:
//   GTLGraderecorderGradeEntry (0 custom class methods, 4 custom properties)

#import "GTLGraderecorderGradeEntry.h"

// ----------------------------------------------------------------------------
//
//   GTLGraderecorderGradeEntry
//

@implementation GTLGraderecorderGradeEntry
@dynamic assignmentKey, entityKey, score, studentKey;

+ (NSDictionary *)propertyToJSONKeyMap {
  NSDictionary *map =
    [NSDictionary dictionaryWithObjectsAndKeys:
      @"assignment_key", @"assignmentKey",
      @"student_key", @"studentKey",
      nil];
  return map;
}

@end
